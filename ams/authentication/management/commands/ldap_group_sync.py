from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django_auth_ldap.backend import LDAPBackend


class Command(BaseCommand):
    help = 'Synchronizes specific LDAP groups with Django groups'

    def handle(self, *args, **options):
        ldap_backend = LDAPBackend()

        # Specify the specific LDAP groups to synchronize
        ldap_groups = [
            'CN=idm-3c9f798c9g2a,OU=IDM,OU=P001,OU=GRP,OU=Data,DC=ericsson,DC=s',
            'CN=oss-sts-support,OU=IDM,OU=P001,OU=GRP,OU=Data,DC=ericsson,DC=se',
        ]

        # Get or create corresponding Django groups
        for ldap_group in ldap_groups:
            group, created = Group.objects.get_or_create(name=ldap_group)

            if created:
                self.stdout.write(f'Created Django group: {group.name}')
            else:
                self.stdout.write(f'Group already exists: {group.name}')