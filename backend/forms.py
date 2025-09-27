from django import forms
from django.core.exceptions import ValidationError
from .models import Surgery, SurgeryName, SurgeryType, Surgeon, SurgerySurgeon
from .functions import get_next_surgery_day


BLOOD_GROUP_CHOICES = [
    (None, "н/о"),
    ("O(I) Rh-", "O(I) Rh-"),
    ("O(I) Rh+", "O(I) Rh+"),
    ("A(II) Rh-", "A(II) Rh-"),
    ("A(II) Rh+", "A(II) Rh+"),
    ("B(III) Rh-", "B(III) Rh-"),
    ("B(III) Rh+", "B(III) Rh+"),
    ("AB(IV) Rh-", "AB(IV) Rh-"),
    ("AB(IV) Rh+", "AB(IV) Rh+"),
]


class SurgeryForm(forms.Form):
    full_name = forms.CharField(max_length=255, strip=True)
    age = forms.IntegerField(required=False)
    diagnost = forms.CharField(max_length=255, strip=True)
    surgery_name = forms.CharField(max_length=255, strip=True)
    surgery_type = forms.CharField(max_length=255, required=False, strip=True)

    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    blood_comment = forms.CharField(max_length=255, required=False, strip=True)

    surgeons = forms.ModelMultipleChoiceField(
        queryset=Surgeon.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    sorted_surgeons = forms.CharField(widget=forms.HiddenInput(), required=False)

    def save(self, commit=True):
        full_name = self.cleaned_data.get('full_name')
        age = self.cleaned_data.get('age')
        diagnost = self.cleaned_data.get('diagnost')
        surgery_name, _ = SurgeryName.objects.get_or_create(surgery_name=self.cleaned_data.get('surgery_name'))
        surgery_type, _ = SurgeryType.objects.get_or_create(type_name=self.cleaned_data.get('surgery_type'))

        bg = (self.cleaned_data.get('blood_group') or "").strip()
        bc = (self.cleaned_data.get('blood_comment') or "").strip()
        bg_combined = f"{bg} | {bc}".strip(" +") if (bg or bc) else None

        surgery = Surgery(
            full_name=full_name,
            age=age,
            diagnost=diagnost,
            surgery_name=surgery_name,
            surgery_type=surgery_type,
            date_of_surgery=get_next_surgery_day(),
            blood_group=bg_combined,
        )

        sorted_surgeons = (self.cleaned_data.get('sorted_surgeons') or "").strip()

        if commit:
            surgery.save()
            if sorted_surgeons:
                for index, surgeon in enumerate(sorted_surgeons.split(',')):
                    SurgerySurgeon.objects.create(surgery=surgery, surgeon_id=int(surgeon), sequence=index)
            return surgery

        return surgery, sorted_surgeons


class SurgeryEditForm(forms.Form):
    full_name = forms.CharField(max_length=255, required=True)
    age = forms.IntegerField(required=False)
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    blood_comment = forms.CharField(max_length=255, required=False, strip=True)
    diagnost = forms.CharField(max_length=255, required=True)
    surgery_name = forms.CharField(max_length=255, required=True)
    surgery_type = forms.CharField(max_length=255, required=False)

    surgeons = forms.ModelMultipleChoiceField(
        queryset=Surgeon.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    sorted_surgeons = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, instance: Surgery = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

        if instance and isinstance(instance, Surgery):
            self.fields['full_name'].initial = instance.full_name
            self.fields['age'].initial = instance.age
            self.fields['diagnost'].initial = instance.diagnost

            self.fields['surgery_name'].initial = (
                instance.surgery_name.surgery_name if instance.surgery_name else ""
            )
            self.fields['surgery_type'].initial = (
                instance.surgery_type.type_name if instance.surgery_type else ""
            )

            self.fields['surgeons'].initial = instance.surgeons.all()

            bg_val = (instance.blood_group or "").strip()
            initial_bg, initial_comment = self._split_blood_group(bg_val)
            self.fields['blood_group'].initial = initial_bg
            self.fields['blood_comment'].initial = initial_comment

    @staticmethod
    def _split_blood_group(value: str) -> tuple[str, str]:
        """
        Saqlangan satr: "{group} + {comment}" yoki faqat "{group}" yoki faqat "{comment}".
        Tanlov bo‘lmagan qismi comment sifatida qabul qilinadi.
        """
        if not value:
            return "", ""
        parts = [p.strip() for p in value.split("|", 1)]
        if len(parts) == 1:
            return (parts[0], "") if parts[0] in dict(BLOOD_GROUP_CHOICES) else ("", parts[0])
        group_part, comment_part = parts[0], parts[1]
        if group_part not in dict(BLOOD_GROUP_CHOICES):
            return ("", value)
        return group_part, comment_part

    @staticmethod
    def _combine_blood_group(group: str | None, comment: str | None) -> str:
        group = (group or "").strip()
        comment = (comment or "").strip()
        if group and comment:
            return f"{group} | {comment}"
        return group or comment or "н/о"

    def clean(self):
        cleaned = super().clean()
        return cleaned

    def save(self) -> Surgery:
        if not self.instance:
            raise ValidationError("SurgeryEditForm.save() uchun instance kerak.")

        self.instance.full_name = self.cleaned_data['full_name']
        self.instance.age = self.cleaned_data.get('age')
        self.instance.diagnost = self.cleaned_data['diagnost']

        surgery_name, _ = SurgeryName.objects.get_or_create(
            surgery_name=self.cleaned_data['surgery_name']
        )
        self.instance.surgery_name = surgery_name

        st_name = (self.cleaned_data.get('surgery_type') or "").strip()
        if st_name:
            surgery_type, _ = SurgeryType.objects.get_or_create(type_name=st_name)
        else:
            surgery_type = None
        self.instance.surgery_type = surgery_type

        combined_bg = self._combine_blood_group(
            self.cleaned_data.get('blood_group'),
            self.cleaned_data.get('blood_comment'),
        )
        self.instance.blood_group = combined_bg or None

        self.instance.save()

        selected_ids = set(self.cleaned_data['surgeons'].values_list('id', flat=True))
        sorted_surgeons_raw = (self.cleaned_data.get('sorted_surgeons') or "").strip()

        self.instance.surgeons.clear()

        if not sorted_surgeons_raw:
            ordered_ids = sorted(selected_ids)
            for idx, sid in enumerate(ordered_ids):
                SurgerySurgeon.objects.create(
                    surgery=self.instance, surgeon_id=int(sid), sequence=idx
                )
            return self.instance

        seq = 0
        for token in sorted_surgeons_raw.split(","):
            token = token.strip()
            if not token:
                continue
            sid = int(token)
            if sid in selected_ids:
                SurgerySurgeon.objects.create(
                    surgery=self.instance, surgeon_id=sid, sequence=seq
                )
                seq += 1

        remaining = [sid for sid in selected_ids if sid not in set(
            int(t.strip()) for t in sorted_surgeons_raw.split(",") if t.strip()
        )]
        for sid in remaining:
            SurgerySurgeon.objects.create(
                surgery=self.instance, surgeon_id=int(sid), sequence=seq
            )
            seq += 1

        return self.instance
