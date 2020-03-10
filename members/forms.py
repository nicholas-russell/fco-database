from django import forms
from allauth.account.forms import SignupForm
from .models import Membership, VolunteerOption
import re

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
    rtn = {
        'valid': True,
        'errors': [],
        'data': {},
        'redirect': None
    }
    phone_pattern = re.compile('^[0-9]{9}$')
    phone_pattern_full = re.compile('^0[0-9]{9}$')
    post_code_pattern = re.compile('^2[0-9]{3}$')

    volunteer_options = VolunteerOption.objects.all()

    if membership_type == "individual":
        user = request.user
        if user is None:
            rtn['valid'] = False
            rtn['errors'].append('There is no logged in user.')
            rtn['redirect'] = 'login'
        try:
            membership = Membership.objects.get(user=user)
        except Membership.DoesNotExist:
            rtn['valid'] = False
            rtn['errors'].append('There is no membership for this user.')
            rtn['redirect'] = 'membership'

        form_data = {
            'membership': membership,
            'phone_number': request.POST.get('phone_number'),
            'post_code': request.POST.get('post_code'),
            'suburb': request.POST.get('suburb'),
            'volunteer_preferences': request.POST.getlist('volunteer_preferences[]'),
            'mailing_list': request.POST.get('mailing_list')
        }

        if form_data['phone_number'] is None or form_data['phone_number'] == "":
            rtn['valid'] = False
            rtn['errors'].append('There is no phone number entered')
        else:
            if phone_pattern_full.match(form_data['phone_number']) is not None:
                form_data['phone_number'] = form_data['phone_number'][1:]
            if phone_pattern.match(form_data['phone_number']) is None:
                rtn['valid'] = False
                rtn['errors'].append('The phone number provided is not a valid Australian number')

        if form_data['post_code'] == "" or form_data['post_code'] is None:
            rtn['valid'] = False
            rtn['errors'].append('There is no postcode entered')
        else:
            if post_code_pattern.match(form_data['post_code']) is None:
                rtn['valid'] = False
                rtn['errors'].append('The postcode entered is not valid')

        if form_data['suburb'] is None or form_data['suburb'] == "":
            rtn['valid'] = False
            rtn['errors'].append('There is no suburb entered')

        if form_data['mailing_list'] is None:
            form_data['mailing_list'] = True
        else:
            form_data['mailing_list'] = False

        for opt in form_data['volunteer_preferences']:
            if volunteer_options.filter(name=opt).count == 0:
                rtn['valid'] = False
                rtn['errors'].append('The volunteer code "{}" is invalid'.format(opt))

        rtn['data'] = form_data
    elif membership_type == "couple":
        pass
    elif membership_type == "household":
        pass
    else:
        rtn['valid'] = False
        rtn['redirect'] = '404'

    return rtn
