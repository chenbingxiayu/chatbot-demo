from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from main.models import StaffStatus

ROLES = [
    ('online_triage', 'Online Triage'),
    ('do', 'DO'),
    ('counsellor', 'Counsellor')
]

STATUS = [
    ('available', 'Available'),
    ('away', 'Away')
]


class LoginForm(forms.Form):
    error_css_class = 'is-invalid'
    required_css_class = 'required'

    netid = forms.CharField(widget=forms.TextInput(attrs={'required': True, 'class': 'form-control'}))
    password = forms.CharField(min_length=8,
                               widget=forms.PasswordInput(attrs={'required': True, 'class': 'form-control'}))
    role = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=ROLES)
    status = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=STATUS)

    def clean_netid(self):
        cleaned_data = super().clean()
        try:
            staff = StaffStatus.objects.get(staff_netid=cleaned_data['netid'].upper())
        except StaffStatus.DoesNotExist as e:
            raise ValidationError("netid or password is incorrect.")

        return staff

    def clean_password(self):
        data = self.cleaned_data['password']
        return data
