from django.test import TestCase
from django.urls import reverse
from PoolTestEnvironment.models import *

class URLTest(TestCase):
    def setUp(self):
        self.cluster = Cluster.objects.create(name='test_cluster')
        # Create a test namespace which will be rolled back after the test is completed
        self.namespace = Namespace.objects.create(name='test_cluster_eic_0',cluster=self.cluster)

    def test_booking_list_url(self):
        response = self.client.get(reverse('pool-test-environment:booking-list'))
        self.assertEqual(response.status_code, 200)

    # def test_create_booking_url_get_method(self):
    #     response = self.client.get(reverse('pool-test-environment:create-booking', args=['test-namespace']))
    #     self.assertEqual(response.status_code, 200)

    # def test_update_booking_url(self):
    #     response = self.client.get(reverse('update-booking', args=['test-namespace']))
    #     self.assertEqual(response.status_code, 200)

    def test_namespace_list_url(self):
        response = self.client.get(reverse('pool-test-environment:namespace-list'))
        self.assertEqual(response.status_code, 200)

    def test_pool_data_url(self):
        response = self.client.get(reverse('pool-test-environment:pool-data'))
        self.assertEqual(response.status_code, 200)

    def test_booking_requests_url(self):
        response = self.client.get(reverse('pool-test-environment:booking-requests'))
        self.assertEqual(response.status_code, 200)

    def test_my_pool_environments_url(self):
        response = self.client.get(reverse('pool-test-environment:my-pool-environments'))
        self.assertEqual(response.status_code, 200)

    # def test_request_pool_environment_url(self):
    #     response = self.client.get(reverse('pool-test-environment:request-pool-environment'))
    #     self.assertEqual(response.status_code, 200)