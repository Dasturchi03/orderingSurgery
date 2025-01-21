from datetime import date, timedelta
from .models import SurgeryDay


def get_or_create_surgery_day(date: date, editable: bool = True):
    try:
        day = SurgeryDay.objects.get(date=date)
    except SurgeryDay.DoesNotExist:
        if date.isoweekday() == 6:
            editable = False
        elif date.isoweekday() == 7:
            return False
        day = SurgeryDay(date=date, editable=editable)
        day.save()
    except Exception as err:
        print(err)
        day, _ = SurgeryDay.objects.get_or_create(date=date)
    return day


def get_next_surgery_day():
    tomorrow = date.today() + timedelta(days=1)
    if tomorrow.isoweekday() == 7:
        tomorrow += timedelta(days=1)
    tw_day = get_or_create_surgery_day(date=tomorrow)

    return tw_day


def get_day(date: date):
    if date.isoweekday() == 7:
        return False
    day = get_or_create_surgery_day(date=date)
    return day


def get_next_30_days():
    days = []
    for i in range(1, 31):
        that_day = date.today() + timedelta(days=i)
        if that_day.isoweekday() == 7:
            continue
        day = get_or_create_surgery_day(date=that_day)
        days.append(day)
    
    return days
