from django.core.management.base import BaseCommand
from manager.models import SystemType, System, Area
import csv
import os, sys

class Command(BaseCommand):

    help = 'Create test_systems in django'
    
    def handle(self, *args, **options):
    # Groups definition

        #System.objects.create(name='stsvp6aenm03', type=SystemType.objects.get(name="vENM"), area=Area.objects.get(name="YOULAB E2E"), admin="Administrator", password="TestPassw0rd")
        #System.objects.create(name='stsvp4enm03', type=SystemType.objects.get(name="vENM"), area=Area.objects.get(name="WELAB"), admin="Administrator", password="TestPassw0rd")
        #self.stdout.write(self.style.SUCCESS('Successfully created objects.'))
        
        filename=os.path.expanduser('~/all_systems.txt')
        if os.path.isfile(filename):
            print("File:",filename,"exist. OK.")
        else:
            print("File:",filename,"doesn't exist. This file should exist and contain systems, area and system types in CSV format:")
            print("<SYSTEM NAME>,<AREA>,<SYSTEM TYPE>")
            print("Example:")
            print("stsvp9enm08,APPLICATION SERVICES,vENM")
            sys.exit(1)

        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                system=row[0]
                area=row[1]
                type=row[2]

                try:
                    enmexist = System.objects.get(name=system)
                except System.DoesNotExist:
                    enmexist = None 

                if enmexist == None:

                    try:
                        areaexist = Area.objects.get(name=area)
                    except:
                        areaexist = None

                    if areaexist == None:
                        print("Area:",area,"doesn't exist and need to be created first.")    
                    else:

                        try:
                            typeexist = SystemType.objects.get(name=type)
                        except:
                            typeexist = None

                        if typeexist == None:
                           print("Type:",type,"doesn't exist and need to be created first.")    
                        else:    
                            print("System:",system,"in Area:",area,"type:",type,"doesn't exist and will be created.")
                            System.objects.create(name=system, type=SystemType.objects.get(name=type), area=Area.objects.get(name=area), admin="Administrator", password="TestPassw0rd")
                            self.stdout.write(self.style.SUCCESS('Successfully created objects.'))                    
                else:
                    print("System:",system,"in Area:",area,"already exist.")
                    