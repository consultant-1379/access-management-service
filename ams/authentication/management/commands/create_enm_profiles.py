from django.core.management.base import BaseCommand
from manager.models import ENMRole,ENMUserProfile

def add_roles(roles_list, profile):
    roles = []
    for name in roles_list:
        try:
            role = ENMRole.objects.get(name=name)
            roles.append(role)
        except role.DoesNotExist:
            print(f"Role with name '{name}' does not exist.")
    profile.schema.add(*roles)

class Command(BaseCommand):
    help = 'Create basic ENM PROFILES in django'
    
    def handle(self, *args, **options):
    # Roles definition
        roles = ['ADMINISTRATOR', 'SECURITY_ADMIN','Cmedit_Administrator','FM_Administrator','Network_Explorer_Administrator','NodeSecurity_Administrator','OPERATOR','Shm_Administrator','Topology_Browser_Administrator','Autoprovisioning_Operator','Autoprovisioning_Administrator','NetworkLog_Administratorr','PKI_EE_Administrator','PKI_Operator','PKI_Administrator','LogViewer_Operator','Amos_Operator','Autoprovisioning_Administrator','Autoprovisioning_Operator','Cmedit_Operator','FM_Operator','Network_Explorer_Operator','Shm_Operator','AddNode_Administrator','ENodeB_Application_Administrator','SupportUnit_Operator', 'CustomRole', 'NetworkLog_Administrator']
        for role in roles:
            obj, created = ENMRole.objects.get_or_create(name=role)
            if created:
                print("Role: " + role + " created")
            else:
                print("Role: " + role + " already exists")

    # Profile definition
        profiles = ['ADMINISTRATOR', 'MANAGEMENT', 'BASIC','SECURITY', 'XFTTEST', 'XFTUSER', 'PICOAI', 'CUSTOM']
        for profile in profiles:
            obj, created = ENMUserProfile.objects.get_or_create(name=profile)
            if created:
                print("Profile: " + profile + " created")
            else:
                print("Role: " + profile  + " already exists")
    
            if profile == "ADMINISTRATOR": 
                add_roles(['ADMINISTRATOR', 'SECURITY_ADMIN'], obj)
            if profile == "MANAGEMENT": 
                add_roles(['ADMINISTRATOR', 'SECURITY_ADMIN','Cmedit_Administrator','FM_Administrator','Network_Explorer_Administrator','NodeSecurity_Administrator','OPERATOR','Shm_Administrator', 'Topology_Browser_Administrator'], obj)
            if profile == "BASIC": 
                add_roles(['Cmedit_Administrator','FM_Administrator','Network_Explorer_Administrator','NodeSecurity_Administrator','OPERATOR','Shm_Administrator', 'Topology_Browser_Administrator','ENodeB_Application_Administrator'], obj)
            if profile == "SECURITY": 
                add_roles(['SECURITY_ADMIN', 'Cmedit_Administrator', 'FM_Administrator', 'Network_Explorer_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Shm_Administrator', 'Topology_Browser_Administrator'], obj)
            if profile == "XFTTEST": 
                add_roles(['Cmedit_Administrator', 'FM_Administrator', 'Network_Explorer_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Shm_Administrator', 'Topology_Browser_Administrator', 'Autoprovisioning_Operator', 'Autoprovisioning_Administrator', 'NetworkLog_Administrator', 'PKI_EE_Administrator', 'PKI_Operator', 'PKI_Administrator', 'AddNode_Administrator'], obj)
            if profile == "XFTUSER": 
                add_roles(['Cmedit_Administrator', 'NodeSecurity_Administrator', 'OPERATOR','Topology_Browser_Administrator', 'LogViewer_Operator', 'AddNode_Administrator'], obj)
            if profile == "PICOAI": 
                add_roles(['SECURITY_ADMIN', 'Cmedit_Administrator', 'FM_Administrator', 'Network_Explorer_Administrator', 'NodeSecurity_Administrator', 'OPERATOR', 'Shm_Administrator', 'Topology_Browser_Administrator', 'Autoprovisioning_Operator', 'Autoprovisioning_Administrator', 'PKI_Administrator', 'Amos_Operator', 'Cmedit_Operator', 'FM_Operator', 'Network_Explorer_Operator', 'Shm_Operator'], obj)