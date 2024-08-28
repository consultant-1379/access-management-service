from django.db import models
from authentication.models import AMSUser
from externalfeeds import encrypt_util
from django.db.models.deletion import ProtectedError
from django.utils import timezone
# Create your models here.

class Area(models.Model):
    name = models.CharField(max_length=200, unique=True)
    users = models.ManyToManyField(AMSUser,  blank=True)

    def delete(self, *args, **kwargs):
        # Check if there relaeted systems
        related_systems = self.system_set.all() 
        if related_systems.exists():
            # Raise a ProtectedError if there are related Systems
            system_names = [system.name for system in related_systems]
            raise ProtectedError("This Area has related Systems and cannot be deleted.",system_names)

        # If no related systems, proceed with deletion
        super(SystemType, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

class Approver (models.Model):
    user = models.OneToOneField(AMSUser, on_delete=models.CASCADE)
    area = models.ManyToManyField(Area)
    def __str__(self):
        return f"{self.user.username}-approver"
    
   
class SystemType(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def delete(self, *args, **kwargs):
        # Check if there relaeted systems
        related_systems = self.system_set.all() 
        if related_systems.exists():
            # Raise a ProtectedError if there are related Systems
            system_names = [system.name for system in related_systems]
            raise ProtectedError("This System Type has related Systems and cannot be deleted.",system_names)

        # If no related systems, proceed with deletion
        super(SystemType, self).delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"

class System (models.Model):
    name = models.CharField(max_length=200, unique=True)
    type = models.ForeignKey(SystemType,on_delete=models.CASCADE, default=None,  blank=True,  null=True)
    area = models.ForeignKey(Area,on_delete=models.CASCADE, default=None,  blank=True,  null=True)
    admin = models.CharField(max_length=50, default=None, null=False)
    password = models.CharField(max_length=512, default=None, null=False)
    status = models.CharField(max_length=256, default=None, null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True)

    def save(self, *args, **kwargs):
        self.password = encrypt_util.encrypt(self.password)
        self.updated_at = timezone.now()  # Update the field before saving
        super(System, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Check if there relaeted systems
        related_accounts = self.account_set.all() 
  
        if related_accounts.exists():
            # Raise a ProtectedError if there are related Systems
            account_names = [account.name for account in related_accounts]
            raise ProtectedError("System set as inactive. This System has related Accounts and cannot be deleted",account_names)
        
        related_orders = self.order_set.all() 
        if related_orders.exists():
            # Raise a ProtectedError if there are related Systems
            order_names = [order.jira_ticket for order in related_orders]
            raise ProtectedError("System set as inactive. This System has related Orders and cannot be deleted",order_names)

        # If no related systems, proceed with deletion
        super(System, self).delete(*args, **kwargs)
    

    def __str__(self):
        return f"{self.name}"
   
class Account (models.Model):
    name = models.CharField(max_length=200, default="<signum>", unique=True)
    user = models.ForeignKey(AMSUser, on_delete=models.CASCADE, default=None, blank=True,  null=True, verbose_name='Owner')
    created_at = models.DateTimeField(auto_now_add=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True)
    systems =  models.ManyToManyField(System, blank=True)
    is_functional_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name}-{self.user.username}"
    
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()  # Update the field before saving
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Check if there relaeted systems
        related_systems = self.system_set.all() 
        if related_systems.exists():
            # Raise a ProtectedError if there are related Systems
            system_names = [system.name for system in related_systems]
            raise ProtectedError("Account set to inactive. Account has related Systems and cannot be deleted.",system_names)
        related_orders = self.order_set.all() 
        if related_orders.exists():
            # Raise a ProtectedError if there are related Orders
            order_names = [order.jira_ticket for order in related_orders]
            raise ProtectedError("Account set as inactive. This Account has related Orders and cannot be deleted",order_names)
        # If no related systems, proceed with deletion
        super(Account, self).delete(*args, **kwargs)

class JiraTicket(models.Model):
    ticket_number = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=1600)
    account =   models.ForeignKey(Account, on_delete=models.CASCADE)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True)
    def __str__(self):
        return f"{self.ticket_number}"
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()  # Update the field before saving
        super().save(*args, **kwargs)
    
class Order (models.Model):
    account =   models.ForeignKey(Account, on_delete=models.CASCADE)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    jira_ticket = models.ForeignKey(JiraTicket, on_delete=models.CASCADE, default=None, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    ordered_by = models.ForeignKey(AMSUser, on_delete=models.CASCADE, default=None, blank=True,  null=True)
    aproved_by = models.ForeignKey(Approver, on_delete=models.CASCADE, default=None, blank=True,  null=True)
    comment = models.CharField(max_length=1600, default="none")
    created_at = models.DateTimeField(auto_now_add=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True)
    def __str__(self):
        return f"{self.jira_ticket.ticket_number}-order"
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()  # Update the field before saving
        super().save(*args, **kwargs)

class ENMRole (models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return f"{self.name}"
    
class EORole (models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return f"{self.name}"
    
class EICRole (models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return f"{self.name}"

class ENMUserProfile (models.Model):
    name = models.CharField(max_length=200, unique=True)
    schema = models.ManyToManyField(ENMRole)
    def __str__(self):
        return f"{self.name}"
    def delete(self, *args, **kwargs):
        # Check if there relaeted user
        related_users = self.enmuser_set.all() 
        if related_users.exists():
            # Raise a ProtectedError if there are related Systems
            user_names = [user.account.name+ " on " + user.system.name  for user in related_users]
            raise ProtectedError("Profile cannot be deleted. There are system account related to his profile: ",user_names)
        super(ENMUserProfile, self).delete(*args, **kwargs)

class ENMUser (models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    profile = models.ForeignKey(ENMUserProfile, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    aproved_by = models.ForeignKey(Approver, on_delete=models.CASCADE, default=None, blank=True,  null=True)
    
    def delete(self, *args, **kwargs):
        if not self.is_approved:
            raise ProtectedError("Cannot delete not approved user",self.account.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.account.name}-{self.system.name}"
    

class EICUserProfile (models.Model):
    name = models.CharField(max_length=200, unique=True)
    schema = models.ManyToManyField(EICRole)
    def __str__(self):
        return f"{self.name}"
    def delete(self, *args, **kwargs):
        # Check if there relaeted user
        related_users = self.eicuser_set.all() 
        if related_users.exists():
            # Raise a ProtectedError if there are related Systems
            user_names = [user.account.name+" on " + user.system.name for user in related_users]
            raise ProtectedError("Profile cannot be deleted. There are system account related to his profile: ",user_names)
        super(EICUserProfile, self).delete(*args, **kwargs)
    

class EICUser (models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    profile = models.ForeignKey(EICUserProfile, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    aproved_by = models.ForeignKey(Approver, on_delete=models.CASCADE, default=None, blank=True,  null=True)
    def __str__(self):
        return f"{self.account.name}"

class EOUserProfile (models.Model):
    name = models.CharField(max_length=200, unique=True)
    schema = models.ManyToManyField(EORole)
    def __str__(self):
        return f"{self.name}"
    def delete(self, *args, **kwargs):
        # Check if there relaeted user
        related_users = self.eouser_set.all() 
        print(related_users)
        if related_users.exists():
            # Raise a ProtectedError if there are related Systems
            user_names = [user.account.name+" on " + user.system.name  for user in related_users]
            raise ProtectedError("Profile cannot be deleted. There are system account related to his profile: ",user_names)
        super(EOUserProfile, self).delete(*args, **kwargs)

class EOUser (models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    profile = models.ForeignKey(EOUserProfile, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    aproved_by = models.ForeignKey(Approver, on_delete=models.CASCADE, default=None, blank=True,  null=True)
    def __str__(self):
        return f"{self.account.name}"

        
     