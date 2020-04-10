from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import response
from django.views import generic
from . import models
from .forms import is_membership_form_valid, is_member_form_valid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
import requests
from querystring_parser import parser

@login_required
def index(request):
    try:
        membership = models.Membership.objects.get(user=request.user)
    except models.Membership.DoesNotExist:
        membership = None

    if membership is None:
        messages.info(request, "You need to add a membership to use your account")
        return redirect('new_membership')

    members = models.Member.objects.filter(membership=membership)
    if not members:
        return redirect("new_membership_details", membership_type=membership.membership_type.url_name())

    context = {
        'membership_type': membership.membership_type.name,
        'membership_expiry': membership.membership_expiry,
        'working_expiry': membership.working_expiry,
        'concession': membership.concession,
        'paid': membership.paid,
        'members': members
    }
    return render(request, "member/member_index.html", {'membership': context})


class NewMembershipDetails(LoginRequiredMixin, generic.View):
    def get(self, request, membership_type):
        volunteer_options = models.VolunteerOption.objects.all()
        context = {
            'volunteer_options': volunteer_options
        }
        if membership_type not in ["individual", "household", "couple"]:
            raise response.Http404()
        return render(request, "member/new_member_" + membership_type + ".html", context)

    def post(self, request, membership_type):
        if membership_type == "individual":
            post_dict = parser.parse(request.POST.urlencode())
            return response.JsonResponse(post_dict, safe=True)
            form = is_member_form_valid(request, membership_type)
            if not form['valid']:
                if form['redirect'] == 'login':
                    return redirect('account_login')
                elif form['redirect'] == 'membership':
                    return redirect('new_membership')
                else:
                    volunteer_options = models.VolunteerOption.objects.all()
                    context = {
                        'volunteer_options': volunteer_options,
                        'form': form
                    }
                    return render(request, "member/new_member_" + membership_type + ".html", context)
            else:
                new_member = models.Member()
                new_member.membership = form['data']['membership']
                new_member.first_name = request.user.first_name
                new_member.last_name = request.user.last_name
                new_member.email = request.user.email
                new_member.phone_number = form['data']['phone_number']
                new_member.postcode = form['data']['post_code']
                new_member.suburb = form['data']['suburb']
                new_member.mailing_list = form['data']['mailing_list']
                new_member.volunteer_preferences = form['data']['volunteer_preferences']
                try:
                    new_member.save()
                    return redirect('member_index')
                except IntegrityError:
                    messages.error(request, "There was an error in the form. Please try again")
                    return redirect("new_membership_details", membership_type)
                except RuntimeError:
                    messages.error(request, "There was an error in the form. Please try again")
                    return redirect("new_membership_details", membership_type)
        elif membership_type == "couple":
            post_dict = parser.parse(request.POST.urlencode())
            return response.JsonResponse(post_dict, safe=True)
        elif membership_type == "household":
            pass
        else:
            raise response.Http404("Invalid membership type")


class NewMembership(LoginRequiredMixin, generic.View):
    def get(self, request):
        try:
            potential_membership = models.Membership.objects.get(user=request.user)
        except models.Membership.DoesNotExist:
            potential_membership = None

        if potential_membership is not None:  # a membership exists
            if models.Member.objects.filter(membership=potential_membership):  # a membership exists with no member details
                messages.info(request, "You already have a membership!")
                return redirect("member_index")
            else:
                messages.info(request, "Please finish your membership application before continuing")
                return redirect("new_membership_details", membership_type=potential_membership.membership_type.url_name())
        context = {
            'membership_types': models.MembershipType.objects.filter(active=True),
            'volunteer_options': models.VolunteerOption.objects.all()
        }
        return render(request, "member/new_membership.html", context)

    def post(self, request):
        post_dict = parser.parse(request.POST.urlencode())
        return response.JsonResponse(post_dict, safe=True)
        if not is_membership_form_valid(request):
            messages.error(request, "There was an error in the form. Please try again")
            return redirect("new_membership")

        data = request.POST
        new_membership = models.Membership()
        new_membership.user = request.user
        new_membership.membership_type = models.MembershipType.objects.get(code=data.get("membership_type"))
        if data.get("concession") is not None:
            if data.get("concession") == "on":
                new_membership.concession = True

        try:
            new_membership.save()
        except IntegrityError:
            messages.error(request, "There was an error in the form. Please try again")
            return redirect("new_membership")
        except RuntimeError:
            messages.error(request, "There was an error in the form. Please try again")
            return redirect("new_membership")

        return redirect("new_membership_details", membership_type=new_membership.membership_type.url_name())


@login_required
def postcode(request, post_code):
    data = requests.get("http://v0.postcodeapi.com.au/suburbs/{}.json".format(post_code))
    return response.HttpResponse(data.content, content_type='application/json')