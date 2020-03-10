from django import forms
from allauth.account.forms import SignupForm
from .models import Membership

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


def is_membership_form_valid(request):
    user = request.user
    membership_type = request.POST.get('membership_type')
    concession_type = request.POST.get('concession_type')

    if user is None:
        return False
    if membership_type is None:
        return False
    if concession_type is not None:
        if concession_type not in Membership.CONCESSION_CODES.values():
            return False

    return True


def is_member_form_valid(request, membership_type):
    return True
