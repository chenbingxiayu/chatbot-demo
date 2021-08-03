from django import forms

ROLES = [
    ('online_triage', 'Online Triage'),
    ('do', 'DO'),
    ('counsellor', 'Counsellor')
]

STATUS = [
    ('available', 'Available'),
    ('away', 'Away')
]


class StaffLoginForm(forms.Form):
    role = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=ROLES)
    status = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=STATUS)
