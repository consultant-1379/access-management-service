from django.core.management.base import BaseCommand
from manager.models import SystemType

class Command(BaseCommand):
    def handle(self, *args, **options):
    # Groups definition

        SystemType.objects.create(name='vENM')
        SystemType.objects.create(name='cENM')
        SystemType.objects.create(name='pENM')
        SystemType.objects.create(name='EO')
        SystemType.objects.create(name='EIC')

        self.stdout.write(self.style.SUCCESS('Successfully created objects.'))