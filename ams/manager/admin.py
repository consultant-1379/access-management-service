from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register([Area, System,SystemType, Account, JiraTicket, Approver,Order,EOUser,EOUserProfile,EICUser,EICUserProfile,ENMUser,ENMRole,ENMUserProfile,EORole,EICRole])