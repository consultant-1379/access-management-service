from statistics import mode
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('', include("home.urls")),
    path('', include("manager.urls")),
    path('api/', include("managerapi.urls")),
    path('', include("PoolTestEnvironment.urls"))
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
