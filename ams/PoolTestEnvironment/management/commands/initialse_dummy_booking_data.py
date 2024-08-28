from django.core.management.base import BaseCommand
from PoolTestEnvironment.models import Cluster, Namespace

class Command(BaseCommand):
    help = 'Seeds the database with dummyy booking pool data'
    
    
    def handle(self, *args, **options):
        # Create some Namespace instances if they don't exist

        namespaces = ["hall115-eric-eic-0", "hall115-eric-eic-1", "hall115-eric-eic-2"]

        # Get the first Namespace
        namespace = Namespace.objects.first()

        # Create some Booking instances and associate them with the first Namespace
        for i in range(3):
            Booking.objects.create(
                namespace=namespace,
                jira_id=f'JIRA-{i}',
                team_name=f'Team {i}',
                team_users=json.dumps(['user1', 'user2']),
                app_set=f'App Set {i}',
                fqdn=f'fqdn{i}.example.com',
                eic_version=f'1.{i}',
                booking_start_date=datetime.now(),
                booking_end_date=datetime.now() + timedelta(days=30),
            )