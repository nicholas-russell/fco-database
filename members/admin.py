from django.contrib import admin
from members import models

admin.site.site_header = "The Food Co-Op Shop & Cafe"
admin.site.title = "The Food Co-Op Shop & Cafe"
admin.site.index_title = "Membership administration"

@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "name",
                    "email",
                    "membership_type",
                    "membership_expiry",
                    "working_expiry",
                    "concession")
    empty_value_display = 'unknown'


@admin.register(models.Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("member_id",
                    "date",
                    "hours",
                    "entered_by")
    empty_value_display = 'unknown'


