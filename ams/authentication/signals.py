from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def add_user_to_group(sender, user, request, **kwargs):

    try:
        if user.is_adminstrator:
            group = Group.objects.get(name="Admins")
            group.user_set.add(user)
        if user.is_operator:
            group = Group.objects.get(name="Operators")
            group.user_set.add(user)
    except Group.DoesNotExist:
        pass