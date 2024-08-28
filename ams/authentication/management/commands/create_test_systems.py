from django.core.management.base import BaseCommand
from manager.models import SystemType, System, Area

class Command(BaseCommand):

    help = 'Create test_systems in django'
    
    def handle(self, *args, **options):
    # Groups definition

        System.objects.create(name='stsvp6aenm03', type=SystemType.objects.get(name="vENM"), area=Area.objects.get(name="YOULAB E2E RADIO"), admin="Administrator", password="TestPassw0rd")
        System.objects.create(name='stsvp4enm03', type=SystemType.objects.get(name="vENM"), area=Area.objects.get(name="WELAB"), admin="Administrator", password="TestPassw0rd")

        self.stdout.write(self.style.SUCCESS('Successfully created objects.'))
