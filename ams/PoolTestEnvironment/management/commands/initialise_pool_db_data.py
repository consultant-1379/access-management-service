from django.core.management.base import BaseCommand
from PoolTestEnvironment.models import Cluster, Namespace


class Command(BaseCommand):
    help = 'Seeds the database with initial pool data'
    
    
    def handle(self, *args, **options):
        def create_clusters(self, *args):
            clusters = ["hall115", "hall133", "hall134", "hall117", "hall116","klug020", "klug021","hall132", "hall137", "hall140", "hall141", "hall144", "hart071", "hart170", "hart171", "hart173", "hart174", "hall122", "hall939", "hall922", "hart098", "hall119", "hart146", "hart147", "hart148", "hart149", "klug031", "klug032", "hall920"]
            
            for cluster in clusters:
                Cluster.objects.create(name=cluster)


        def create_namespaces(self, *args):
            namespaces = ["hall115-eric-eic-0", "hall115-eric-eic-1", "hall115-eric-eic-2", "hall115-eric-eic-3", "hall115-eric-eic-4", "hall115-eric-eic-5", "hall137-eric-eic-0", "hall137-eric-eic-1", "hall137-eric-eic-2", "hall137-eric-eic-3", "hall140-eric-eic-0", "hall140-eric-eic-1", "hall140-eric-eic-2", "hall140-eric-eic-3", "hall140-eric-eic-4", "hall141-eric-eic-0", "hall141-eric-eic-1", "hall141-eric-eic-2", "hall144-eric-eic-0", "hall144-eric-eic-1", "hall144-eric-eic-2", "hall144-eric-eic-3", "hart071-eric-eic-0", "hart071-eric-eic-1", "hart071-eric-eic-2", "hart071-eric-eic-3", "hart071-eric-eic-4", "hart071-eric-eic-5", "hart170-eric-eic-0", "hart170-eric-eic-1", "hart170-eric-eic-2", "hart170-eric-eic-3", "hart170-eric-eic-6", "hart171-eric-eic-0", "hart171-eric-eic-1", "hart171-eric-eic-2", "hart171-eric-eic-3", "hart173-eric-eic-0", "hart173-eric-eic-1", "hart173-eric-eic-2", "hart173-eric-eic-3", "hart173-eric-eic-4", "hart173-eric-eic-5", "hart174-eric-eic-0", "hart174-eric-eic-1", "hart174-eric-eic-2", "hart174-eric-eic-3", "hart174-eric-eic-4", "hall122-eric-eic-0", "hall122-eric-eic-1", "hall122-eric-eic-2", "hall122-eric-eic-3", "hall939-eric-eic-1", "hall939-eric-eic-0", "hall922-eric-eic-0", "hall922-eric-eic-1", "hall922-eric-eic-2", "hall922-eric-eic-3", "hart098-eric-eic-0", "hart098-eric-eic-1", "hart098-eric-eic-2", "hart098-eric-eic-3", "hart098-eric-eic-4", "hall119-eric-eic-0", "hall119-eric-eic-1", "hall119-eric-eic-2", "hall119-eric-eic-3", "hart146-eric-eic-0", "hart146-eric-eic-1", "hart146-eric-eic-2", "hart146-eric-eic-3", "hart147-eric-eic-0", "hart147-eric-eic-1", "hart147-eric-eic-2", "hart147-eric-eic-3", "hart148-eric-eic-0", "hart148-eric-eic-1", "hart148-eric-eic-2", "hart148-eric-eic-3", "hart149-eric-eic-0", "hart149-eric-eic-1", "hart149-eric-eic-2", "hart149-eric-eic-3", "klug031-eric-eic-0", "klug031-eric-eic-1", "klug031-eric-eic-2", "klug031-eric-eic-3", "klug031-eric-eic-4", "klug031-eric-eic-5", "klug032-eric-eic-0", "klug032-eric-eic-1", "klug032-eric-eic-2", "klug032-eric-eic-3", "klug032-eric-eic-4", "klug032-eric-eic-5", "klug032-eric-eic-6", "hall920-eric-eic-0", "hall920-eric-eic-1", "hall920-eric-eic-2", "hall920-eric-eic-3","klug021-eric-eic-0","klug021-eric-eic-1","klug021-eric-eic-2","klug021-eric-eic-3","klug021-eric-eic-4","klug021-eric-eic-5","klug021-eric-eic-6","klug020-eric-eic-0","klug020-eric-eic-1","klug020-eric-eic-2","klug020-eric-eic-3","klug020-eric-eic-4","klug020-eric-eic-5","klug020-eric-eic-6","hall116-eric-eic-0","hall116-eric-eic-1","hall116-eric-eic-2","hall117-eric-eic-0","hall117-eric-eic-1","hall117-eric-eic-2","hall132-eric-eic-0","hall132-eric-eic-1","hall132-eric-eic-2","hall132-eric-eic-3","hall133-eric-eic-0","hall133-eric-eic-1","hall133-eric-eic-2","hall133-eric-eic-3","hall134-eric-eic-0","hall134-eric-eic-1","hall134-eric-eic-2","hall134-eric-eic-3","hall135-eric-eic-0","hall135-eric-eic-1","hall135-eric-eic-2","hall135-eric-eic-3","hall136-eric-eic-0","hall136-eric-eic-1","hall136-eric-eic-2","hall136-eric-eic-3"]

            for namespace in namespaces:
                cluster_name = namespace.split("-")[0]
                try:
                    cluster = Cluster.objects.get(name=cluster_name)
                except Cluster.DoesNotExist:
                    cluster = None

                if cluster is not None:
                    print(cluster.name)
                else:
                    print('No cluster found with name')
                
                # Check if namespace already exists
                try:
                    if Namespace.objects.filter(name=namespace).exists():
                        print("Namespace already exists")
                    else:
                        print(f"Namespace does not exist. Creating now for ns {namespace}")
                        Namespace.objects.create(name=namespace, cluster=cluster)
                except Exception as e:
                    print(e)
        
        # create_clusters(self)
        create_namespaces(self)