from django.core.management.base import BaseCommand
from PoolTestEnvironment.models import Team
import pandas as pd
import openpyxl
import ast 


class Command(BaseCommand):
    help = 'Seeds the database with initial pool team data'
    
    
    def handle(self, *args, **options):

        def create_teams(self, *args):
            df = pd.read_excel('PoolTestEnvironment/management/commands/data/pool_team_data.xlsx')
            df['users'] = df['users'].apply(ast.literal_eval)

            instances = []

            
            for index, row in df.iterrows():
                
                data = {
                    'name': row['name'],
                    'users': row['users'],
                    'email': row['email'],
                    'project_manager': row['project_manager'],
                }

                # ** Unpacks dict data into django model
                instances.append(Team(**data))

            Team.objects.bulk_create(instances)
        
        def fix_user_format_issue(self, *args):
            instances = Team.objects.all()

            for instance in instances:
                # Only add teams that have been added correctly here e.g. Don't need to be fixed.
                if instance.name != "Muon": 
                    # Convert the string representation of the list into an actual list - Fix pandas mistake
                    instance.users = ast.literal_eval(instance.users)
                    instance.save()
        
        # Run the create teams function
        create_teams(self)
        # fix_user_format_issue(self) # Uncomment if you need to apply users db fix