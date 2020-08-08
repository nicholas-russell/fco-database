from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import response
from django.views import generic
from . import models
from .forms import MembershipForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
import requests
from querystring_parser import parser
from django.core.exceptions import PermissionDenied


@login_required
def index(request):
    try:
        membership = models.Membership.objects.get(user=request.user)
    except models.Membership.DoesNotExist:
        membership = None

    if membership is None:
        return redirect('new_membership')

    members = models.Member.objects.filter(membership=membership)
    context = {
        'membership': membership,
        'members': members
    }
    return render(request, "member/member_index.html", context)


class NewMembership(LoginRequiredMixin, generic.View):
    def get(self, request, form=None):
        try:
            potential_membership = models.Membership.objects.get(user=request.user)
        except models.Membership.DoesNotExist:
            potential_membership = None

        if potential_membership is not None:  # a membership exists
            if models.Member.objects.filter(
                    membership=potential_membership):  # a membership exists with no member details
                messages.info(request, "You already have a membership!")
                return redirect("member_index")
            else:
                messages.info(request, "Please finish your membership application before continuing")

        return self.show_form(request, form)

    def show_form(self, request, form):
        context = {
            'membership_types': models.MembershipType.objects.filter(active=True),
            'volunteer_options': models.VolunteerOption.objects.all(),
            'form': form
        }
        return render(request, "member/new_membership.html", context)

    def post(self, request):
        form = MembershipForm(parser.parse(request.POST.urlencode()))

        if not form.valid:
            messages.error(request, "There was an error in the form. Please try again")
            return self.get(request, form.data)

        new_membership = models.Membership()
        new_membership.user = request.user
        new_membership.membership_type = models.MembershipType.objects.get(code=form.membership_type)
        new_membership.concession = form.concession
        new_membership.concession_type = form.concession_type

        try:
            new_membership.save()
        except IntegrityError:
            messages.error(request, "There was an error in the form. Please try again")
            return self.get(request, form.data)
        except RuntimeError:
            messages.error(request, "There was server error. Please try again later")
            return self.get(request, form.data)

        new_members = []
        for member in form.members:
            new_member = models.Member.objects.create(**member, membership=new_membership)
            new_members.append(new_member)

        for member_model in new_members:
            try:
                member_model.save()
            except IntegrityError:
                messages.error(request, "There was an error in the form. Please try again")
                print(new_membership)
                new_membership.delete()
                return self.get(request, form.data)
            except RuntimeError:
                messages.error(request, "There was server error. Please try again later")
                print(new_membership)
                new_membership.delete()
                return self.get(request, form.data)

        return redirect("member_index")


@login_required
def postcode(request, post_code):
    data = requests.get("http://v0.postcodeapi.com.au/suburbs/{}.json".format(post_code))
    return response.HttpResponse(data.content, content_type='application/json')


class ViewMembership(LoginRequiredMixin, generic.View):
    def get(self, request, member_id=None, form=None):
        if member_id is None:
            try:
                membership = models.Membership.objects.get(user=request.user)
            except models.Membership.DoesNotExist:
                return NewMembership.show_form(request)
        else:
            try:
                membership = models.Membership.objects.get(pk=member_id)
            except models.Membership.DoesNotExist:
                raise response.Http404

        members = models.Member.objects.filter(membership=membership)
        # TODO: add payments model here
        context = {
            'membership': membership,
            'members': members,
            'volunteer_options': models.VolunteerOption.objects.all(),
            'form': form,
            # TODO: add boolean if more members are able to be put on membership
        }
        return render(request, "member/view_membership.html", context)

    def post(self, request):
        pass


class ViewMember(LoginRequiredMixin, generic.View):
    def get(self, request, member_id):
        try:
            member = models.Member.objects.get(pk=member_id)
        except models.Member.DoesNotExist:
            raise response.Http404

        try:
            membership = models.Membership.objects.get(user=request.user)
        except models.Membership.DoesNotExist:
            raise response.Http404

        if member.membership != membership:
            raise PermissionDenied
        else:
            context = {
                'volunteer_options': models.VolunteerOption.objects.all(),
                'member': member
            }
            return render(request, "member/view_member.html", context)

    def post(self, request, member_id):
        pass


class NewMember(LoginRequiredMixin, generic.View):
    def get(self, request, form):
        pass

    def post(self, request, form):
        pass
