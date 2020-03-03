from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import response
from django.views import generic
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def index(request):
    try:
        membership = models.Membership.objects.get(user=request.user)
    except models.Membership.DoesNotExist:
        membership = None

    if membership is None:
        return redirect('new_membership')
    else:
        context = {
            'membership_type': membership.get_membership_type_display(),
            'membership_expiry': membership.membership_expiry,
            'working_expiry': membership.working_expiry,
            'concession': membership.concession,
            'paid': membership.paid
        }
        return render(request, "member/member_index.html", {'membership': context})


class NewMembershipDetails(LoginRequiredMixin, generic.View):
    def get(self, request, membership_type):
        volunteer_options = models.VolunteerOption.objects.all()
        data = {
            'volunteer_options': volunteer_options
        }
        return response.HttpResponse(membership_type)

    def post(self, request, membership_type):
        post_data = request.POST
        html = ""
        html += "Membership type: " + membership_type
        for key, value in list(post_data.items()):
            if key == "volunteer_preferences[]":
                html += "<p><strong>" + key + ":</strong> " + ', '.join(post_data.getlist(key)) + "</p>"
            else:
                html += "<p><strong>" + key + ":</strong> " + value + "</p>"
        return response.HttpResponse(html)


class NewMembership(LoginRequiredMixin, generic.View):
    def get(self, request):
        return render(request, "member/new_membership.html")

    def post(self, request):
        post_data = request.POST
        html = ""
        for key, value in list(post_data.items()):
            html += "<p><strong>" + key + ":</strong> " + value + "</p>"
        return response.HttpResponse(html)