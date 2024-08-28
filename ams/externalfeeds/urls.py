from django.urls import path
from . import views

urlpatterns = [
    path('report', views.get_report),
    path('run', views.get_data),
]