from django.core.management.base import BaseCommand
from manager.models import AMSUser,ENMUser,ENMUserProfile,Account,System
import csv
import sys, os

class Command(BaseCommand):
    help = 'Import ENM users into django'
    

    def handle(self, *args, **options):
        filename=os.path.expanduser('~/all_enm_userlist_with_privileges.txt')

        if os.path.isfile(filename):
            print("File:",filename,"exist. OK.")
        else:
            print("File:",filename,"doesn't exist. This file should exist and contain users with system and roles in CSV format:")
            print("<USERNAME>,<ENM NAME>,<ROLE1, ROLE2, .., ROLE(N)>")
            print("Example:")
            print("zraklzb,stscenm.n107p2,SECURITY_ADMIN,ADMINISTRATOR")
            sys.exit(1)

        profiles= {
            'ADMINISTRATOR':['ADMINISTRATOR', 'SECURITY_ADMIN'],
            'MANAGEMENT':	['ADMINISTRATOR', 'SECURITY_ADMIN', 'Cmedit_Administrator', 'FM_Administrator', 'Network_Explorer_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Shm_Administrator', 'Topology_Browser_Administrator'],
            'BASIC':		['Cmedit_Administrator', 'FM_Administrator', 'Network_Explorer_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Shm_Administrator', 'Topology_Browser_Administrator', 'ENodeB_Application_Administrator'],
            'SECURITY':		['SECURITY_ADMIN', 'Cmedit_Administrator', 'FM_Administrator', 'Network_Explorer_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Shm_Administrator', 'Topology_Browser_Administrator'],
            'XFTTEST':		['Cmedit_Administrator', 'FM_Administrator', 'Network_Explorer_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Shm_Administrator', 'Topology_Browser_Administrator', 'Autoprovisioning_Operator', 'Autoprovisioning_Administrator', 'NetworkLog_Administrator', 'PKI_EE_Administrator', 'PKI_Operator', 'PKI_Administrator', 'AddNode_Administrator'],
            'XFTUSER':		['Cmedit_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Topology_Browser_Administrator', 'LogViewer_Operator', 'CustomRole', 'AddNode_Administrator'],
            'PICOAI':		['SECURITY_ADMIN', 'Cmedit_Administrator', 'FM_Administrator', 'Network_Explorer_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Shm_Administrator', 'Topology_Browser_Administrator', 'Autoprovisioning_Operator', 'Autoprovisioning_Administrator', 'PKI_Administrator', 'Amos_Operator', 'Cmedit_Operator', 'FM_Operator', 'Network_Explorer_Operator', 'Shm_Operator'],
            'CUSTOM':       [''],
        }

        def find_profile(inputitem):
            found=False
#            username=inputitem[0]
#            system=inputitem[1]
            rolelist=inputitem[2:]
            rolelist.sort()

            for key, value in list(profiles.items()): 
                value.sort()

                if value == rolelist:
 #                   print("Create account for:",username,"on ENM:",system,"with profile:",key)
                    found=True
                    return key
                
            if not found:
 #               print("Create account for:",username,"on ENM:",system,"with profile: CUSTOM")
                return "CUSTOM"

##BODY            
        #input=['zraklzb','stscenm.n107p2','SECURITY_ADMIN','ADMINISTRATOR']
        #input=['erubchr','stsvp9enm34','NodeSecurity_Administrator','Topology_Browser_Administrator','Network_Explorer_Administrator','OPERATOR','ENodeB_Application_Administrator','FM_Administrator','Shm_Administrator','Cmedit_Administrator']
        #find_profile(input)
        missingprofiles=False

        for key, value in list(profiles.items()):

            try:
                profileexist = ENMUserProfile.objects.get(name=key)
            except:
                profileexist = None

            if profileexist == None:
                print("Profile:", key,"doesn't exist. Create it first.")
                missingprofiles=True
        
        if missingprofiles == True:
            print("Exiting.")
            sys.exit(2)

        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                username=row[0]
                systemname=row[1]
                profilename=find_profile(row)

                try:
                    system = System.objects.get(name=systemname)
                except:
                    system = None
                
                if system == None:
                    print("Can't add user - system:",systemname,"doesn't exist. Create it first.")
                    continue

                try:
                    profile = ENMUserProfile.objects.get(name=profilename)
                except:
                    profile = None

                try:
                    amsuser = AMSUser.objects.get(username = username)
                except AMSUser.DoesNotExist:
                    amsuser = None 

                if amsuser == None :
                    print("creating AMSUser:: " + username)
                    amsuser = AMSUser(
                    username = username,
                    )
                    amsuser.save()

                try:
                    account =  Account.objects.get(name = username)
                except Account.DoesNotExist:
                    account = None 

                if account == None :
                    print("creating Account:: " + username)
                    account = Account(
                    name = username,
                    user = amsuser,
                    is_functional_user = False,
                    )
                account.save()
                account.systems.add(system)
                account.save()

                if not ENMUser.objects.filter( system = system, account = account).exists() :

                    print("Create account for:",username,"on ENM:",systemname,"with profile:",profilename)
                    system_account = ENMUser(
                                account = account,
                                profile = profile, 
                                system = system,
                                is_approved = True,
                                # aproved_by = current_user, ## need to find a better way to set who approved account
                            )
                    system_account.save()
                else:
                        print("ENM user:",username,"on system:",systemname,"already exists")