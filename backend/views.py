import json
import logging
from collections import defaultdict
from datetime import date, timedelta, datetime

from django.db.models import Prefetch
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse
from django.http.request import HttpRequest, UnreadablePostError
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect

from .forms import SurgeryForm, SurgeryEditForm
from .models import Surgery, Branch, SurgeryName, SurgeryType, Surgeon, SurgeryDay, SurgerySurgeon
from .functions import get_next_surgery_day, get_day, get_or_create_surgery_day

from weasyprint import HTML


logger = logging.getLogger('__main__')
dir_ = 'staticfiles/fonts/'


def home(request: HttpRequest):
    date_param = request.GET.get('date')
    if date_param:
        try:
            selected_date = date.fromisoformat(date_param)
        except ValueError:
            selected_date = None
    else:
        selected_date = None

    if selected_date:
        day = get_day(selected_date)
        if not day:
            branches = []
        else:
            branches = Branch.objects.prefetch_related(
                Prefetch(
                    'surgeries',
                    queryset=Surgery.objects.filter(date_of_surgery=day)
                    .order_by('seq_number')
                    .prefetch_related(
                        Prefetch(
                            'surgeons',
                            queryset=Surgeon.objects.all().order_by('surgerysurgeon__sequence'),
                            to_attr='ordered_surgeons'
                        )
                    )
                )
            ).order_by('branch_number')

    else:
        day = get_next_surgery_day()
        logger.info(day)
        branches = Branch.objects.prefetch_related(
            Prefetch(
                'surgeries',
                queryset=Surgery.objects.filter(date_of_surgery=day)
                .order_by('seq_number')
                .prefetch_related(
                    Prefetch(
                        'surgeons',
                        queryset=Surgeon.objects.all().order_by('surgerysurgeon__sequence'),
                        to_attr='ordered_surgeons'
                    )
                )
            )
        ).order_by('branch_number')

    if branches and request.user.is_authenticated:
        qs = branches.filter(heads=request.user)
        if request.user.is_superuser:
            pass
        elif qs:
            branches = qs

    return render(request, 'index.html', {'branches': branches, 'day': day})


@csrf_exempt
def update_surgery_seq(request: HttpRequest):
    if request.method == 'POST' and request.user.is_superuser:
        data: dict = json.loads(request.body)
        surgery_id = data.get('surgery_id')
        new_seq_number = data.get('new_seq_number')
        new_branch_number = data.get('new_branch_number')

        try:
            surgery = Surgery.objects.get(id=surgery_id)
            old_branch = surgery.branch
            new_branch = Branch.objects.get(branch_number=int(new_branch_number))

            if old_branch.pk != new_branch.pk:
                surgery.branch_id = new_branch.pk

            surgery.seq_number = int(new_seq_number)
            surgery.save()

            surgeries = Surgery.objects.filter(branch_id=old_branch.id).exclude(id=surgery.id).order_by('seq_number')
            for index, item in enumerate(surgeries, start=1):
                item.seq_number = index
                item.save()
                logger.info(f'{item.seq_number} old')

            surgeries_in_new_branch = Surgery.objects.filter(branch_id=new_branch.pk).exclude(id=surgery.id).order_by('seq_number')
            for index, item in enumerate(surgeries_in_new_branch, start=1):
                if index >= int(new_seq_number):
                    item.seq_number = index + 1
                    item.save()
                    logger.info(f'{item.seq_number} new')

            return JsonResponse({'success': True})
        except Surgery.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Surgery not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})


def profile(request: HttpRequest):
    user = request.user.username
    return HttpResponse({'user': user})


def add_surgery(request: HttpRequest, branch_id):
    date_str = request.GET.get('date')
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            day = get_or_create_surgery_day(date=date_obj)
            if not day:
                raise ValueError
        except ValueError:
            return HttpResponse("Invalid date format.", status=400)
    else:
        day = get_next_surgery_day()
    branch = get_object_or_404(Branch, id=branch_id)
    surgery_names = SurgeryName.objects.all()
    surgery_types = SurgeryType.objects.all()
    surgeons = Surgeon.objects.filter(branch=branch).order_by('full_name')

    if request.method == 'POST':
        form = SurgeryForm(request.POST)

        if form.is_valid():
            surgery, sorted_surgeons = form.save(commit=False)
            surgery.branch = branch
            surgery.own_branch = branch
            surgery.date_of_surgery = day
            surgery.seq_number = Surgery.objects.filter(branch__id=branch_id).filter(date_of_surgery=day).count() + 1
            surgery.save()
            for index, surgeon in enumerate(sorted_surgeons.split(',')):  
                SurgerySurgeon.objects.create(surgery=surgery, surgeon_id=int(surgeon), sequence=index)
            return HttpResponseRedirect(f'/?date={date_str}')
        else:
            logger.error(form.errors)
            raise UnreadablePostError("Form is not valid!")
    else:
        form = SurgeryForm()

    context = {
        'form': form,
        'branch': branch,
        'surgery_names': surgery_names,
        'surgery_types': surgery_types,
        'surgeons': surgeons,
    }
    return render(request, 'add_surgery.html', context)


def search_surgery_name(request: HttpRequest):
    query = request.GET.get('query', '').lower()

    if query:
        results = SurgeryName.objects.all()
        results = [i for i in results if query in i.surgery_name.lower()][:10]
        data = [{'id': item.id, 'surgery_name': item.surgery_name} for item in results]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def search_surgery_type(request: HttpRequest):
    query = request.GET.get('query', '').lower()
    if query:
        results = SurgeryType.objects.filter()
        results = [i for i in results if query in i.type_name.lower()][:10]
        data = [{'id': item.id, 'type_name': item.type_name} for item in results]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def edit_surgery(request: HttpRequest, surgery_id: int):
    surgery = get_object_or_404(Surgery, id=surgery_id)
    branch = Branch.objects.get(pk=surgery.branch.pk)

    if request.method == 'POST':
        form = SurgeryEditForm(request.POST, instance=surgery)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SurgeryEditForm(instance=surgery)

    context = {
        'form': form,
        'surgery': surgery,
        'surgeons': Surgeon.objects.filter(branch=branch),
        'branch': branch,
    }
    return render(request, 'edit_surgery.html', context)


def delete_surgery(request: HttpRequest, surgery_id: int):
    surgery = get_object_or_404(Surgery, id=surgery_id)
    if request.method == 'POST':
        surgery.delete()
    return redirect('home')


@csrf_exempt
def update_seq_number(request: HttpRequest):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            for item in data:
                surgery = Surgery.objects.get(id=item['id'])
                surgery.seq_number = item['seq_number']
                surgery.save()
            return JsonResponse({"success": True}, status=200)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


def change_editable_surgeryday(request: HttpRequest, surgeryday_id: int):
    if request.user.is_superuser:
        day = SurgeryDay.objects.get(pk=surgeryday_id)
        day.editable += 1 - day.editable * 2
        day.save()
    return redirect('/')


def generate_pdf(request: HttpRequest):
    date_str = request.GET.get('date')
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            day = get_or_create_surgery_day(date=date_obj)
            if not day:
                raise ValueError
        except ValueError:
            return HttpResponse("Invalid date format.", status=400)
    else:
        day = get_next_surgery_day()

    if request.user.is_authenticated:
        try:
            if request.user.is_superuser:
                branches = Branch.objects.prefetch_related('surgeries').order_by('branch_number')
            else:
                branches = Branch.objects.prefetch_related('surgeries'
                                                            ).filter(heads=request.user
                                                                ).order_by('branch_number')
        except Exception as err:
            branches = Branch.objects.prefetch_related('surgeries').order_by('branch_number')
            logger.error(err)
    else:
        return HttpResponse('Not found')

    WEEKDAYS_RU = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    date_str = day.date.strftime('%d.%m.%Y')
    weekday_str = WEEKDAYS_RU[day.date.weekday()]

    branches_data = []
    for branch in branches:
        assert isinstance(branch, Branch)
        surgeries = branch.surgeries.filter(date_of_surgery=day).order_by('seq_number')
        surgeries_data = []
        for surgery in surgeries:
            assert isinstance(surgery, Surgery)
            surgeons = [surgeon.full_name for surgeon in surgery.surgeons.all()]
            surgeries_data.append({
                "number": f"{branch.branch_number}.{surgery.seq_number}",
                "notes": surgery.surgery_type.type_name if surgery.surgery_type else "-",
                "department": surgery.own_branch.name,
                "patient_name": surgery.full_name,
                "age": str(surgery.age) if surgery.age else "-",
                "blood_group": surgery.blood_group if surgery.blood_group else "-",
                "diagnosis": surgery.diagnost,
                "operation_name": surgery.surgery_name.surgery_name,
                "surgeons": surgeons,
            })
        if surgeries_data:
            branches_data.append({
                "page_number": branch.page_number,
                "branch_number": branch.branch_number,
                "surgeries": surgeries_data,
            })

    pages = sorted({j["page_number"] for j in branches_data})

    content = {
        "date": date_str,
        "weekday": weekday_str,
        "branches": branches_data,
        "pages": pages,
        "last_page": pages[-1]
    }

    html_content = render_to_string("pdf_template.html", content)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="operations_{day.date}.pdf"'
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(response)
    return response
