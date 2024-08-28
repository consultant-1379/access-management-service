import site
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files import File
from django.conf import settings
# Create your views here.


def index(request):

    title1= "home"
    subtitle1 = "STS NM Access Management Service"
    title2= "Changelog"
    subtitle2 = ""
    title3= "Links"
    subtitle3 = ""
    content3 =""

    return render(request, "home.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "title2": title2,
        "subtitle2": subtitle2,
        "title3": title3,
        "subtitle3": subtitle3,

    })


def about(request):

    title1= "About site"
    subtitle1 = "Our Team"
    title2= "Areas and Approvers"
    subtitle2 = ""

    title3= "Open Issues"
    subtitle3 = ""


    return render(request, "about.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "title2": title2,
        "subtitle2": subtitle2,
        "title3": title3,
        "subtitle3": subtitle3,

    })
