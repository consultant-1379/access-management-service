import django_tables2 as tables
from django_tables2 import TemplateColumn
from .models import *
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, IntegerField
from prometheus_api_client import PrometheusConnect
from PoolTestEnvironment.constants import values
from django.utils.html import format_html

class BookingRequestsTable(tables.Table):
    actions = TemplateColumn(template_name='booking-request-actions.html', orderable=False)

    class Meta:
        model = Booking
        attrs = {"class": "table", "id": "row-actions-example"}
        fields = ('name', 'team', 'app_set', 'booking_end_date', 'jira_id', 'booking_end_date','tls_enabled')
        orderable = True

# My Pool Environment View - table 2
class MyBookingRequestsTable(BookingRequestsTable):
    actions = TemplateColumn(template_name='my-booking-requests-actions.html', orderable=False)

    class Meta:
        attrs = attrs = {"class": "table", "id": "row-actions-example"}

class NamespaceTable(tables.Table):
    name = tables.Column(verbose_name="Namespace")
    team = tables.Column(accessor='booking.team.name',verbose_name="Team")  
    app_set = tables.Column(accessor='booking.app_set')  
    tls_enabled = tables.Column(accessor='booking.tls_enabled',verbose_name="TLS Enabled") 
    booking_end_date = tables.Column(accessor='booking.booking_end_date')  
    jira_id = tables.Column(accessor='booking.jira_id')
    days_remaining = tables.Column(empty_values=())
    graphana_link = tables.Column(verbose_name="Grafana Link",empty_values=())  
    # cluster_name = name.split('-')[0]
    # url = values.POOL_GRAFANA_URL
    # graphana_link = tables.TemplateColumn('<a href="{{ record.get_absolute_url }}">{{ record.name }}</a>', orderable=False)


    actions = TemplateColumn(template_name='pool_actions_column.html', orderable=False)

    def render_days_remaining(self, record):
        try:
            booking = record.booking
            if booking and booking.booking_end_date:
                now = timezone.now().date()
                return (booking.booking_end_date - now).days
        except Exception as e:
            print(f"Error calculating days remaining: {e}")
        return 0
    
    def order_days_remaining(self, QuerySet, is_descending):
        QuerySet = QuerySet.annotate(
            days_remaining=ExpressionWrapper(F('booking__booking_end_date') - timezone.now().date(), output_field=IntegerField())
        ).order_by(('-' if is_descending else '') + 'days_remaining')
        return (QuerySet, True)

    def render_graphana_link(self, record):
        link = values.POOL_GRAFANA_URL.format(cluster_name=record.cluster.name,namespace=record.name)
        return format_html('<a href="{}">Monitoring</a>', link)

    #     def getPrometheusConnection():
    #         print("Creating the prometheus client")
    #         prom_client = PrometheusConnect(url=values.PROMETHEUS_URI, disable_ssl=True)
    #         return prom_client

    #     def getTotalCpu(clusterid):

    #         client = getPrometheusConnection()

    #         print("Retrieving Total CPU")
    #         query = f"sum(kube_node_status_allocatable{{program=~'DETS', cluster_id=~'{clusterid}', resource='cpu'}})"
    #         total_cpu = client.custom_query(query=query)

    #         if len(total_cpu) < 1 or "value" not in total_cpu[0] or len(total_cpu[0]["value"]) < 2:
    #             print(f"Query is {query}")
    #             raise Exception(f"Unexpected data structure : {total_cpu}")

    #         total_cpu_val = total_cpu[0]["value"][1]
    #         rounded_value = round(float(total_cpu_val), 1)
    #         print(f"Total CPU: {rounded_value}")
    #         return rounded_value

    #     def getUsedCpu(clusterid):

    #         client = getPrometheusConnection()

    #         # ns_string = 'All'
    #         ns_string = 'hart148-eric-eic-6'
    #         # ns_string = 'kube-system|hart148-eric-eic-0|hart148-eric-eic-1|hart148-eric-eic-2|dets-monitoring|ingress-nginx|gatekeeper-system'

    #         print("Retrieving Used CPU from Prometheus")
    #         query = f"sum(kube_pod_container_resource_requests{{vpod='EIAP',dc='ews0', program=~'DETS', cluster_id=~'{clusterid}', resource='cpu', namespace=~'({ns_string})'}})"
    #         # query = f"sum(kube_pod_container_resource_requests{{vpod='EIAP',dc='ews0', program=~'DETS', cluster_id=~'{clusterid}', resource='cpu', namespace=~'{ns_string})'}}".format(clusterid,ns_string)
    #         used_cluster_CPU = client.custom_query(query=query)

    #         if len(used_cluster_CPU) < 1 or "value" not in used_cluster_CPU[0] or len(used_cluster_CPU[0]["value"]) < 2:
    #             print(f"Query is {query}")
    #             raise Exception(f"Unexpected data structure : {used_cluster_CPU}")

    #         used_cluster_cpu_val = used_cluster_CPU[0]["value"][1]
    #         rounded_value = round(float(used_cluster_cpu_val), 1)
    #         print(f"Used CPU: {rounded_value}")
    #         return rounded_value

    #     try:
    #         cluster_name = record.cluster.name
    #         print(record)
    #         print("Booking cluster name is: ",cluster_name)
    #         cpu_remaining = getTotalCpu(cluster_name) - getUsedCpu(cluster_name)
    #         return cpu_remaining
        
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
        
    #     return 0
        
            

    class Meta:
        model = Namespace
        attrs = attrs = {"class": "table", "id": "row-actions-example"}
        fields = ('name', 'team', 'app_set', 'tls_enabled', 'booking_end_date', 'jira_id', 'days_remaining')
        orderable = True

class MyPoolEnvironmentsTable(NamespaceTable):
    actions = TemplateColumn(template_name='my-pool-environments-actions.html', orderable=False)

    class Meta:
        attrs = attrs = {"class": "table", "id": "row-actions-example"}

