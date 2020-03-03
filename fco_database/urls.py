from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from members import views as members_views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('allauth.urls')),
    path('', members_views.index, name='member_index'),
    path('membership/new/', members_views.NewMembership.as_view(), name='new_membership'),
    path('membership/new/<str:membership_type>/', members_views.NewMembershipDetails.as_view(),
         name="new_membership_details")
]
