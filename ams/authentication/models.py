from django.db import models
from django.contrib.auth.models import AbstractUser

class AMSUser(AbstractUser):
   is_adminstrator = models.BooleanField(default=False)
   is_operator = models.BooleanField(default=False)
   is_approver = models.BooleanField(default=False)
   is_pool_user = models.BooleanField(default=False)
   is_pool_admin = models.BooleanField(default=False)

   