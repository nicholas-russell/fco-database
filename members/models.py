from django.db import models
from django.contrib.auth.models import User
from fco_database.lib import RandomFileName
from enum import Enum
from django.contrib.postgres.fields import ArrayField
from django_enum_choices.fields import EnumChoiceField


class MembershipType(models.Model):
    name = models.CharField(max_length=32)
    code = models.CharField(max_length=1)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    concession_price = models.DecimalField(max_digits=5, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Member(models.Model):

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
    concession = models.BooleanField(default=False)
    concession_proof = models.ImageField(upload_to=RandomFileName('concession_images'), blank=True, null=True)
    concession_type = models.CharField(max_length=1, choices=concession_choices, null=True, blank=True)
    suburb = models.CharField(max_length=32, null=True, blank=True)
    postcode = models.CharField(max_length=4, null=True, blank=True)
    phone_number = models.CharField(max_length=9, null=True, blank=True)
    mailing_list = models.BooleanField(default=True)
    volunteer_preferences = ArrayField(models.CharField(max_length=3), null=True, blank=True)

    membership_expiry = models.DateField(null=True, blank=True)
    working_expiry = models.DateField(null=True, blank=True)
    membership_approved = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
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

