from django.contrib import admin
from .models import HydraInfo, DTTInfo, DITInfo
# Register your models here.
admin.site.register([HydraInfo, DTTInfo, DITInfo])
