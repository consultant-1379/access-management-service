from django.core.management.base import BaseCommand
from manager.models import Area

class Command(BaseCommand):
    help = 'Create basic Areas in django'
    
    def handle(self, *args, **options):
    # Groups definition

        #Area.objects.create(name='YOULAB E2E')
        Area.objects.create(name='YOULAB E2E RADIO')
        Area.objects.create(name='YOULAB E2E PC')
        Area.objects.create(name='WELAB')
        Area.objects.create(name='APPLICATION SERVICES')
        Area.objects.create(name='LEARNING SERVICES')

        self.stdout.write(self.style.SUCCESS('Successfully created objects.'))