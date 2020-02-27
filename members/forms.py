from django import forms
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First name', widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, label='Last name', widget=forms.TextInput(attrs={'placeholder': 'Last name'}))

    field_order = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def signup(self, request, user):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user
