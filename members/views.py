from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import response
from django.views import generic
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def index(request):
    try:
        member = models.Member.objects.get(user=request.user)
    except models.Member.DoesNotExist:
        member = None

    if member is None:
        return redirect('new_member')
    else:
        context = {
            'user_email': member.user.email,
            'membership_type': member.get_membership_type_display(),
            'membership_expiry': member.membership_expiry,
            'working_expiry': member.working_expiry,
            'concession': member.concession,
            'paid': member.paid
        }
        return render(request, "member/member_index.html", {'member': context})


class NewMember(LoginRequiredMixin, generic.View):
    def get(self, request):
        volunteer_options = models.VolunteerOption.objects.all()
        data = {
            'volunteer_options': volunteer_options
        }
        return render(request, "member/new_member.html", data)

    def post(self, request):
        post_data = request.POST
        html = ""
        print(post_data.getlist('volunteer_preferences[]'))
        for key, value in list(post_data.items()):
            if key == "volunteer_preferences[]":
                html += "<p><strong>" + key + ":</strong> " + ', '.join(post_data.getlist(key)) + "</p>"
            else:
                html += "<p><strong>" + key + ":</strong> " + value + "</p>"
        return response.HttpResponse(html)