from django.urls import path, include
from manager.models import *
from manager.serializers import *
from rest_framework import routers, viewsets

#Instance View set
class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class =  SystemSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class =  AccountSerializer

    

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'systems',SystemViewSet)
router.register(r'accounts',AccountViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]