from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
# Handling this in backend instead of signals
    # def ready(self):
    #     import authentication.signals 
