from django.core.management.base import BaseCommand
from PoolTestEnvironment.models import Booking,Namespace,Team
import pandas as pd
import openpyxl
import ast 
from datetime import datetime , date


class Command(BaseCommand):
    help = 'Seeds the database with initial pool bookings'
    
    
    def handle(self, *args, **options):

        def create_bookings(self, *args):
            try:
                df = pd.read_excel('PoolTestEnvironment/management/commands/data/pool_bookings.xlsx')
                
                for index, row in df.iterrows():

                    # Get the Namespace and Team objects
                    print(row['namespace'])
                    namespace = Namespace.objects.get(name=row['namespace'])
                    team = Team.objects.get(name=row['team'])
                    print(team)

                    date = datetime.strptime(row['end_date'],'%d-%m-%Y')
                    end_date = date.strftime('%Y-%m-%d')
                    print(end_date)
                    today = date.today()
                    start_date = today.strftime('%Y-%m-%d')
                    
                    try:
                        Booking.objects.create(
                            team = team,
                            namespace = namespace,
                            app_set = row['app_set'],
                            booking_end_date = end_date,
                            jira_id = row['jira_id'],
                            booking_start_date = start_date
                        )
                    
                    except Exception as e:
                        print("Error with creating booking ", e)

                    
                    
                    
            except Exception as e:
                print("Error ", e)
        
        # Run the create teams function
        create_bookings(self)
        