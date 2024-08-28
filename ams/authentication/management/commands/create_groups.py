from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


def add_app_permissions_to_admin_group(app_name, group_name):
    #all content types
    app_content_types = ContentType.objects.filter(app_label=app_name)

    # Create or retrieve the group
    group, created = Group.objects.get_or_create(name=group_name)

    # Loop through each content type and add its permissions to the group
    for content_type in app_content_types:
        app_permissions = Permission.objects.filter(content_type=content_type)
        for permission in app_permissions:
            group.permissions.add(permission)

    # Print a message to indicate success
    if created:
        print(f"Group '{group_name}' created and permissions added.")
    else:
        print(f"Permissions added to existing group '{group_name}'.")



class Command(BaseCommand):
    help = 'Create basic groups in django'
    
    def handle(self, *args, **options):
    # Groups definition
        operators_group, created = Group.objects.get_or_create(name="Operators")
        approvers_group, created = Group.objects.get_or_create(name="Approvers")
        add_app_permissions_to_admin_group( "manager", "Admins")
