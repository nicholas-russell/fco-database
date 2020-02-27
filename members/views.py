from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import response
from django.views import generic
from . import models


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


class NewMember(generic.View):
    def get(self, request):
        return response.HttpResponse("this is a get")

    def post(self, request):
        return response.HttpResponse("this is a post")