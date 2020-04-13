from django import forms
from allauth.account.forms import SignupForm
from .models import Membership, VolunteerOption
import re


class MembershipForm:

    def __init__(self, data):
        self.valid = True
        self.errors = []

        self.member_fields = ['first_name', 'last_name', 'phone_number', 'postcode',
                              'suburb', 'email', 'mailing_list', 'volunteer_preferences']

        self.members = []
        self.member_count = None
        self.membership_type = None
        self.concession = False
        self.concession_type = None
        self.data = data
        if self.validate_structure():
            self.parse()
            self.validate_members()
        else:
            self.__error__("Invalid form structure")

    def parse(self):
        self.membership_type = self.data['membership_type']
        if 'concession_type' in self.data:
            self.concession_type = self.data['concession_type']
            self.concession = True
        if self.membership_type == 'h':
            self.member_count = min(int(self.data['household_members']), 5)
        elif self.membership_type == 'i':
            self.member_count = 1
        elif self.membership_type == 'c':
            self.member_count = 2
        else:
            self.__error__("Bad form structure")

        for i in range(1, self.member_count + 1):
            self.members.append(self.data['member'][i])

        for i, member in enumerate(self.members):
            if 'volunteer_preferences' not in member:
                self.members[i]['volunteer_preferences'] = []
            elif type(member['volunteer_preferences']) == str:
                self.members[i]['volunteer_preferences'] = [member['volunteer_preferences']]
            if 'mailing_list' not in member:
                self.members[i]['mailing_list'] = True
            else:
                self.members[i]['mailing_list'] = False
            self.members[i]['phone_number'] = member['phone_number'].replace(" ", "")


    def validate_structure(self):
        if 'membership_type' not in self.data:
            return False
        elif self.data['membership_type'] not in ['i', 'c', 'h']:
            return False
        elif self.data['membership_type'] == 'h':
            if 'household_members' not in self.data:
                return False
        if 'member' not in self.data:
            return False
        if 'concession_type' in self.data:
            if self.data['concession_type'] not in Membership.CONCESSION_CODES.values():
                return False
        return True

    def validate_members(self):
        volunteer_options = VolunteerOption.objects.all()
        email_re = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
            r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)
        for i, member in enumerate(self.members):
            if all(field in member and not self.empty(field) for field in self.member_fields):
                if len(member['first_name']) > 35:
                    self.__error__("First name is too long")
                if len(member['last_name']) > 35:
                    self.__error__("Last name is too long")
                if email_re.match(member['email']) is None:
                    self.__error__("Email is an incorrect format")
                if len(member['phone_number']) > 16:
                    self.__error__("Phone number is too long")
                if len(member['postcode']) > 4:
                    self.__error__("Postcode is too long")
                if len(member['suburb']) > 32:
                    self.__error__("Suburb is too long")
                if type(member['mailing_list']) is not bool:
                    self.__error__("Invalid form data")
                for opt in member['volunteer_preferences']:
                    if volunteer_options.filter(name=opt).count == 0:
                        self.__error__("Volunteer option is not valid")
            else:
                self.__error__("Missing form fields")

    def __str__(self):
        return f'MembershipForm\n' \
               f'===================\n' \
               f'valid: {self.valid}\n' \
               f'errors: {self.errors}\n\n' \
               f'member_count: {self.member_count}\n' \
               f'membership_type: {self.membership_type}\n' \
               f'concession: {self.concession}\n' \
               f'concession_type: {self.concession_type}\n' \
               f'members: {self.members}\n' \
               f'members_n: {len(self.members)}'

    def __error__(self, message=None):
        self.valid = False
        if message is not None:
            self.errors.append(message)

    @staticmethod
    def empty(data):
        return data is None or data == ""


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
    postcode_pattern = re.compile('^2[0-9]{3}$')

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
            'postcode': request.POST.get('postcode'),
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

        if form_data['postcode'] == "" or form_data['postcode'] is None:
            rtn['valid'] = False
            rtn['errors'].append('There is no postcode entered')
        else:
            if postcode_pattern.match(form_data['postcode']) is None:
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
