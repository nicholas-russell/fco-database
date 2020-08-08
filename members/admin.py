from django.contrib import admin
from members import models

admin.site.site_header = "The Food Co-Op Shop & Cafe"
admin.site.title = "The Food Co-Op Shop & Cafe"
admin.site.index_title = "Membership administration"


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("membership", "first_name", "last_name", "email", "phone_number")


@admin.register(models.Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "membership_type", "concession", "membership_expiry", "working_expiry", "paid")


@admin.register(models.Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("member",
                    "date",
                    "hours")
    empty_value_display = 'unknown'


@admin.register(models.VolunteerOption)
class VolunteerOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "info")


@admin.register(models.MembershipType)
class MembershipTypesAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "price", "concession_price", "active")
