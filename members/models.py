from django.db import models
from django.contrib.auth.models import User
from fco_database.lib import RandomFileName
# Create your models here.


class Member(models.Model):
    membership_choices = [
        ("i", "Individual"),
        ("c", "Couple"),
        ("h", "Household"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=1, choices=membership_choices, default="i")
    membership_expiry = models.DateField(null=True, blank=True)
    working_expiry = models.DateField(null=True, blank=True)
    membership_approved = models.BooleanField(default=False)
    concession = models.BooleanField(default=False)
    concession_proof = models.ImageField(upload_to=RandomFileName('concession_images'), blank=True, null=True)
    ts_entered = models.DateTimeField(auto_now_add=True)
    ts_updated = models.DateTimeField(auto_now=True)


class Shift(models.Model):
    member_id = models.ForeignKey(Member, on_delete=models.DO_NOTHING)
    date = models.DateField()
    hours = models.DecimalField(decimal_places=1, max_digits=3)
    entered_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ts_entered = models.DateTimeField(auto_now_add=True)
    ts_updated = models.DateTimeField(auto_now=True)