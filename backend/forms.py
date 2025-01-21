from django import forms
from .functions import get_next_surgery_day
from .models import Surgery, SurgeryName, SurgeryType, Surgeon
from datetime import date


class SurgeryForm(forms.Form):
    full_name = forms.CharField(max_length=255, strip=True)
    age = forms.IntegerField(required=False)
    diagnost = forms.CharField(max_length=255, strip=True)
    surgery_name = forms.CharField(max_length=255, strip=True)
    surgery_type = forms.CharField(max_length=255, required=False, strip=True)
    surgeons = forms.ModelMultipleChoiceField(
        queryset=Surgeon.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def save(self, commit=True):
        full_name = self.cleaned_data.get('full_name')
        age = self.cleaned_data.get('age')
        diagnost = self.cleaned_data.get('diagnost')
        surgery_name, _ = SurgeryName.objects.get_or_create(surgery_name=self.cleaned_data.get('surgery_name'))
        surgery_type, _ = SurgeryType.objects.get_or_create(type_name=self.cleaned_data.get('surgery_type'))
        surgeons = self.cleaned_data.get('surgeons')
        date_of_surgery = get_next_surgery_day()

        surgery = Surgery(
            full_name=full_name,
            age=age,
            diagnost=diagnost,
            surgery_name=surgery_name,
            surgery_type=surgery_type,
            date_of_surgery=date_of_surgery,
        )

        if commit:
            surgery.save()
            surgery.surgeons.set(surgeons)
            return surgery
        
        return surgery, surgeons


class SurgeryEditForm(forms.Form):
    full_name = forms.CharField(max_length=255, required=True)
    age = forms.IntegerField(required=False)
    diagnost = forms.CharField(max_length=255, required=True)
    surgery_name = forms.CharField(max_length=255, required=True)
    surgery_type = forms.CharField(max_length=255, required=False)
    surgeons = forms.ModelMultipleChoiceField(
        queryset=Surgeon.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, instance: Surgery = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        if instance and isinstance(instance, Surgery):
            self.fields['full_name'].initial = instance.full_name
            self.fields['age'].initial = instance.age
            self.fields['diagnost'].initial = instance.diagnost
            self.fields['surgery_name'].initial = instance.surgery_name.surgery_name
            self.fields['surgery_type'].initial = instance.surgery_type.type_name
            self.fields['surgeons'].initial = instance.surgeons.all()

    def save(self):
        if self.instance:
            self.instance.full_name = self.cleaned_data['full_name']
            self.instance.age = self.cleaned_data['age']
            self.instance.diagnost = self.cleaned_data['diagnost']
            surgery_name, _ = SurgeryName.objects.get_or_create(surgery_name=self.cleaned_data['surgery_name'])
            surgery_type, _ = SurgeryType.objects.get_or_create(type_name=self.cleaned_data['surgery_type'])
            self.instance.surgery_name = surgery_name
            self.instance.surgery_type = surgery_type
            self.instance.save()
            self.instance.surgeons.set(self.cleaned_data['surgeons'])
        return self.instance
