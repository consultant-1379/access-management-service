from django.core.management.base import BaseCommand
from django.contrib.auth import AMSUser
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Creates a functional user and generates a token for it'

    def handle(self, *args, **options):
        User = AMSUser()
        user, created = User.objects.get_or_create(username='jenkins', defaults={'password':'password'})
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created functional user.'))
        else:
            self.stdout.write(self.style.WARNING('Functional user already exists.'))

        token, created = Token.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created token.'))
        else:
            self.stdout.write(self.style.WARNING('Token already exists.'))

        self.stdout.write('Token: ' + token.key)