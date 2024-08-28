from django.db import models
import socket

class Cluster(models.Model):
    name = models.CharField(max_length=50)
    cpu_available = models.IntegerField(default=0)
    memory_available = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class Namespace(models.Model):
    name = models.CharField(max_length=100)
    cluster = models.ForeignKey(Cluster, related_name='namespaces', on_delete=models.CASCADE)
    ip = models.CharField(max_length=20,default='')
    fqdn = models.CharField(max_length=100,default='')
    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    users = models.JSONField()
    email = models.EmailField()
    project_manager = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Booking(models.Model):
    # relaated name allows you to access in reverse other models e.g namespace.bookings.all() or namespace.clusters.all()
    namespace = models.OneToOneField(Namespace, related_name='booking', on_delete=models.CASCADE, null=True, blank=True)
    jira_id = models.CharField(max_length=50)
    team = models.ForeignKey(Team, related_name='bookings', on_delete=models.CASCADE,null=True)
    eic_version = models.CharField(max_length=50,default='')
    booking_start_date = models.DateField()
    booking_end_date = models.DateField()
    tls_enabled = models.BooleanField(default=False)
    app_set = models.CharField(max_length=100)
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('SUCCEEDED', 'Succeeded'),
        ('FAILED', 'Failed'),
    ]
    cpu_required = models.IntegerField(default=0)
    memory_required = models.IntegerField(default=0)
    
    booking_status = models.CharField(max_length=12,
        choices=STATUS_CHOICES,
        default='IN_PROGRESS',
    )

    def calculate_requirements(self):
        cpu_required = 0
        memory_required = 0
        print(self.app_set)
        app_names = self.app_set.split(' ')

        for app_name in app_names:
            try:
                print(app_name)
                app = App.objects.get(name=app_name.strip())  
                print(app.cpu_required)
                cpu_required += app.cpu_required
                memory_required += app.memory_required
            except App.DoesNotExist:  
                pass
        print(f"CPU required is {cpu_required}. Memory required is {memory_required}")
        return cpu_required, memory_required

    # def get_ip_address(self):
    #     try:
    #         self.ip = socket.gethostbyname(self.fqdn)
    #         self.save()
    #         return self.ip
    #     except socket.gaierror:
    #         return None
    
    def __str__(self):
        return "{} - {}".format(self.jira_id, self.namespace)
    
class App(models.Model):
    name = models.CharField(max_length=50)
    cpu_required = models.IntegerField(default=0)
    memory_required = models.IntegerField(default=0)
    # app_set_name = models.CharField(max_length=50)
    
    def __str__(self):
        return "{}".format(self.name)

# Uncomment later on redesign
# class Apps(models.Model):
#     name = models.CharField(max_length=50)
#     description = models.CharField(max_length=50)
#     cpu_required = models.IntegerField()
#     memory_required = models.IntegerField()
#     app_set_tag = models.CharField(max_length=50)
    
#     def __str__(self):
#         return "{} - {}".format(self.name, self.app_set_tag)