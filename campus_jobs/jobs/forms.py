import re
from django import forms

from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["full_name", "email", "phone", "cover_letter"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "input"}),
            "email": forms.EmailInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input"}),
            "cover_letter": forms.Textarea(attrs={"class": "textarea", "rows": 8}),
        }

    def clean_full_name(self):
        value = self.cleaned_data["full_name"].strip()
        if len(value) < 3:
            raise forms.ValidationError("Имя и фамилия должны быть не короче 3 символов.")
        return value

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        if not re.fullmatch(r"[0-9+\-() ]{7,20}", value):
            raise forms.ValidationError("Введите корректный номер телефона.")
        return value

    def clean_cover_letter(self):
        value = self.cleaned_data["cover_letter"].strip()
        if len(value) < 50:
            raise forms.ValidationError("Сопроводительное письмо должно быть не короче 50 символов.")
        return value