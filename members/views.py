from django.shortcuts import render
from django.http import response


def index(request):
    return response.HttpResponse("test")

