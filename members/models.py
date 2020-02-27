from django.db import models
from django.contrib.auth.models import User
from fco_database.lib import RandomFileName
from enum import Enum
from django.contrib.postgres.fields import ArrayField
from django_enum_choices.fields import EnumChoiceField
# Create your models here.


class Member(models.Model):
    class MembershipTypes(Enum):
        INDIVIDUAL = "Individual"
        COUPLE = "Couple"
        HOUSEHOLD = "Household"
        PHIL = "Philanthropic"

    class ConcessionTypes(Enum):
        STUDENT = "Student"
        PENSION = "Pension"
        HEALTHCARE = "Healthcare"
        OTHER = "Other"

    membership_choices = [
        (MembershipTypes.INDIVIDUAL.value, "Individual"),
        (MembershipTypes.COUPLE.value, "Couple"),
        (MembershipTypes.HOUSEHOLD.value, "Household"),
        (MembershipTypes.PHIL.value, "Philanthropic")
    ]
    concession_choices = [
        (ConcessionTypes.STUDENT.value, "Student"),
        (ConcessionTypes.PENSION.value, "Pension"),
        (ConcessionTypes.HEALTHCARE.value, "Healthcare"),
        (ConcessionTypes.OTHER.value, "Other")
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # membership_type = models.CharField(max_length=1, choices=membership_choices, default="i")
    membership_type = EnumChoiceField(MembershipTypes)
    membership_expiry = models.DateField(null=True, blank=True)
    working_expiry = models.DateField(null=True, blank=True)
    membership_approved = models.BooleanField(default=False)
    concession = models.BooleanField(default=False)
    concession_proof = models.ImageField(upload_to=RandomFileName('concession_images'), blank=True, null=True)
    # concession_type = models.CharField(max_length=1, choices=concession_choices, blank=True, null=True)
    concession_type = EnumChoiceField(ConcessionTypes, null=True, blank=True)
    suburb = models.CharField(max_length=32, null=True, blank=True)
    postcode = models.CharField(max_length=4, null=True, blank=True)
    phone_number = models.CharField(max_length=9, null=True, blank=True)
    paid = models.BooleanField(default=False)
    mailing_list = models.BooleanField(default=True)
    volunteer_preferences = ArrayField(models.CharField(max_length=3), null=True, blank=True)
    ts_entered = models.DateTimeField(auto_now_add=True)
    ts_updated = models.DateTimeField(auto_now=True)

    def name(self):
        return self.user.first_name + " " + self.user.last_name

    def email(self):
        return self.user.email

    def __str__(self):
        return self.user.email


class Shift(models.Model):
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING)
    date = models.DateField()
    hours = models.DecimalField(decimal_places=1, max_digits=3)
    entered_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ts_entered = models.DateTimeField(auto_now_add=True)
    ts_updated = models.DateTimeField(auto_now=True)


class VolunteerOption(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=32)
    info = models.TextField(blank=True, null=True)
