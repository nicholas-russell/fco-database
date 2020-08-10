from django.db import models
from django.contrib.auth.models import User
from fco_database.lib import RandomFileName
from django.contrib.postgres.fields import ArrayField
from datetime import date
from .volunteer import calc_new_volunteer_expiry


class MembershipType(models.Model):
    name = models.CharField(max_length=32)
    code = models.CharField(max_length=1)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    concession_price = models.DecimalField(max_digits=5, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def url_name(self):
        return self.name.lower()


class Membership(models.Model):
    CONCESSION_CODES = {
        "STUDENT": "s",
        "PENSION": "p",
        "HEALTHCARE": "h",
        "OTHER": "o"
    }
    concession_choices = [
        (CONCESSION_CODES["STUDENT"], "Student"),
        (CONCESSION_CODES["PENSION"], "Pension"),
        (CONCESSION_CODES["HEALTHCARE"], "Healthcare"),
        (CONCESSION_CODES["OTHER"], "Other")
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.SET("OLD_MEMBERSHIP"))
    membership_expiry = models.DateField(null=True, blank=True)
    working_expiry = models.DateField(null=True, blank=True)
    concession = models.BooleanField(default=False)
    concession_proof = models.ImageField(upload_to=RandomFileName('concession_images'), blank=True, null=True)
    concession_type = models.CharField(max_length=1, choices=concession_choices, null=True, blank=True)
    paid = models.BooleanField(default=False)
    membership_active = models.BooleanField(default=False)
    ts_entered = models.DateTimeField(auto_now_add=True)
    ts_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    @property
    def has_working_discount(self):
        if self.working_expiry is None:
            return False
        else:
            return self.working_expiry >= date.today()

    @staticmethod
    def get_membership_from_user(user):
        return Membership.objects.get(user=user)

    @property
    def can_add_member(self):
        members_count = Member.objects.filter(membership=self).count()
        print(self.membership_type.__str__())
        if self.membership_type.__str__() == "Individual":
            return members_count < 1
        elif self.membership_type.__str__() == "Couple":
            return members_count < 2
        elif self.membership_type.__str__() == "Household":
            return members_count < 5
        else:
            return False


class Member(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    email = models.EmailField()
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    postcode = models.CharField(max_length=4, null=True, blank=True)
    suburb = models.CharField(max_length=32, null=True, blank=True)
    mailing_list = models.BooleanField(default=True)
    volunteer_preferences = ArrayField(models.CharField(max_length=32), null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    @staticmethod
    def get_form_fields():
        #return [getattr(field, field.name) for field in Member._meta.get_fields()].remove("membership")
        return ["first_name", "last_name", "email", "phone_number",
                "postcode", "suburb", "mailing_list", "volunteer_preferences"]


class Shift(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(decimal_places=1, max_digits=3)
    #entered_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ts_entered = models.DateTimeField(auto_now_add=True)
    ts_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(Shift, self).save(*args, **kwargs)
        membership = self.member.membership
        member_number = Member.objects.filter(membership=membership).count()
        membership.working_expiry = calc_new_volunteer_expiry(self.hours, membership.working_expiry, member_number)
        membership.save()


class VolunteerOption(models.Model):
    name = models.CharField(max_length=32)
    info = models.TextField(blank=True, null=True)
