from django.db import models
from manager.models import *

# Create your models here.
class HydraInfo (models.Model):
    json_data = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE, default=None, blank=True,  null=True)
    def __str__(self):
        return f"{self.id}"    

class DTTInfo (models.Model):
    json_data = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE, default=None, blank=True,  null=True)
       
    def __str__(self):
        return f"{self.id}"    


class DITInfo (models.Model):
    json_data = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE, default=None, blank=True,  null=True)
    
    def __str__(self):
        return f"{self.id}"    