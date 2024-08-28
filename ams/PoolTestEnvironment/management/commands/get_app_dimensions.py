from django.core.management.base import BaseCommand
from PoolTestEnvironment.models import App
import json



class Command(BaseCommand):
    help = ''
    
    
    def handle(self, *args, **options):
        def create_cluster_dimensions_document(self, *args):
            apps = App.objects.all()
            data = {}
            for app in apps:
                data[app.name] = {
                    'cpu_required' : app.cpu_required,
                    'memory_required' : app.memory_required
                }
            
            with open('PoolTestEnvironment/management/commands/data/dimensions.json','w') as f:
                json.dump(data,f, indent=4)

        create_cluster_dimensions_document(self)