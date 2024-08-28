from django.shortcuts import render

# Create your views here.
def get_data(request):
    return render(request, "inventory.page.tmpl.html",{})
    
#This will read last report from DB
def get_report(request):
    return render(request, "inventory.page.tmpl.html",{})