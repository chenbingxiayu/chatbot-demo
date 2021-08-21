from django import forms

ROLES = [
    ('online_triage', 'Online Triage'),
    ('do', 'DO'),
    ('counsellor', 'Counsellor')
]

SUPERVISOR_ROLES = [
    ('supervisor', 'Supervisor')
] + ROLES

ADMIN_ROLES = [
    ('admin', 'Administrator')
] + SUPERVISOR_ROLES

STATUS = [
    ('available', 'Available'),
    ('away', 'Away')
]


class StaffLoginForm(forms.Form):
    role = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=ROLES)
    status = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=STATUS)

    def __init__(self, user_group: str, *args, **kwargs):
        super(StaffLoginForm, self).__init__(*args, **kwargs)
        if user_group == 'app_admin':
            self.fields['role'].choices = ADMIN_ROLES
        elif user_group == 'supervisor':
            self.fields['role'].choices = SUPERVISOR_ROLES
