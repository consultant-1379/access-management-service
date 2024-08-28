from django.urls import path
from PoolTestEnvironment.views import *

app_name = 'pool-test-environment'

urlpatterns = [
    path('api/bookings/', BookingList.as_view(), name='booking-list'),
    path('api/booking/', BookingAPIView.as_view(), name='create-booking'),
    path('api/booking/<str:namespace>/', BookingAPIView.as_view(), name='update-booking'),
    path('api/namespaces/', NamespaceList.as_view(), name='namespace-list'),
    path('pool-deployments/', NamespaceTableView.as_view(), name='pool-data'),
    path('pool-deployments/booking-requests', BookingRequestsTableView.as_view(), name='booking-requests'),
    path('pool-deployments/trigger_jenkins/', TriggerJenkinsView.as_view(), name='trigger-jenkins'),
    path('pool-deployments/my-environments/', MyPoolEnvironmentsView.as_view(), name='my-pool-environments'),
    path('pool-deployments/my-environments/order', RequestEnvironmentView.as_view(), name='request-pool-environment'),
    path('pool-deployments/booking/update/<int:pk>/', BookingUpdateView.as_view(), name='pool-booking-update'),
    path('pool-deployments/booking-requests/update/<int:pk>/', AssignNamespaceToBookingView.as_view(), name='assign-namespace-to-booking'),
]

