from django.test import TestCase, Client
from django.urls import reverse
from PoolTestEnvironment.models import *
from PoolTestEnvironment.views import BookingRequestsTableView
from datetime import date
from authentication.models import AMSUser
from django.utils import timezone




class BookingRequestsTableViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        try:
            self.url = reverse('pool-test-environment:booking-requests')
            self.cluster = Cluster.objects.create(name='test_cluster')
            self.namespace = Namespace.objects.create(name='test_cluster_eic_0',cluster=self.cluster)
            self.team = Team.objects.create(name='Test Team',users=[""],email="x@gmail.com",project_manager="pm")
        except Exception as e:
            self.fail(f'Setup failed: {e}')

    def test_view_status_code(self):
        try:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            self.fail(f'test_view_status_code failed: {e}')

    def test_view_uses_correct_template(self):
        try:
            response = self.client.get(self.url)
            self.assertTemplateUsed(response, 'booking-requests.html')
        except Exception as e:
            self.fail(f'test_view_uses_correct_template failed: {e}')

    def test_view_returns_only_namespace_null_bookings(self):
        try:
            today = date.today()
            # Create a booking with namespace=None
            Booking.objects.create(namespace=None,jira_id='test',team=self.team,booking_start_date=today,booking_end_date=today,app_set='')
            # Create a booking with namespace not None
            Booking.objects.create(namespace=self.namespace,jira_id='test',team=self.team,booking_start_date=today,booking_end_date=today,app_set='')

            response = self.client.get(self.url)
            bookings = response.context['object_list']

            self.assertTrue(all(booking.namespace is None for booking in bookings))
        except Exception as e:
            self.fail(f'test_view_returns_only_namespace_null_bookings failed: {e}')

class MyPoolEnvironmentsTableViewTest(TestCase):
    def setUp(self):
        # Create users
        self.user1 = AMSUser.objects.create_user(username='testuser1', password='12345',is_pool_user=True)
        self.user2 = AMSUser.objects.create_user(username='testuser2', password='12345',is_pool_user=True)

        # Create cluster, teams and namespaces for each user
        self.cluster = Cluster.objects.create(name='test_cluster')
        self.namespace1 = Namespace.objects.create(name='test_cluster_eic_0',cluster=self.cluster)
        self.namespace2 = Namespace.objects.create(name='test_cluster_eic_2',cluster=self.cluster)
        self.team1 = Team.objects.create(name='Test Team 2',users=[self.user1.username],email="x@gmail.com",project_manager="pm")
        self.team2 = Team.objects.create(name='Test Team 2',users=[self.user2.username],email="x@gmail.com",project_manager="pm")
        
        # Create a Booking instances
        self.booking1 = Booking.objects.create(
            namespace=self.namespace1,
            jira_id='testjira',
            team=self.team1,
            fqdn='test.fqdn.com',
            eic_version='0.0.0',
            booking_start_date=timezone.now().date(),
            booking_end_date=timezone.now().date(),
            tls_enabled=True,
            app_set='testapp'
        )

        self.booking2 = Booking.objects.create(
            namespace=self.namespace2,
            jira_id='testjira',
            team=self.team2,
            fqdn='test.fqdn.com',
            eic_version='0.0.0',
            booking_start_date=timezone.now().date(),
            booking_end_date=timezone.now().date(),
            tls_enabled=True,
            app_set='testapp'
        )

    def test_view_success_status_code(self):
        self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('pool-test-environment:my-pool-environments'))  
        self.assertEqual(response.status_code, 200)

    def test_view_correct_namespaces(self):
        self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('pool-test-environment:my-pool-environments'))  
        self.assertContains(response, 'test_cluster_eic_0')
        self.assertNotContains(response, 'test_cluster_eic_2')

    # def test_view_redirect_if_not_logged_in(self):
    #     response = self.client.get(reverse('pool-test-environment:my-pool-environments'))  
    #     self.assertEqual(response.status_code, 302)

    def test_view_uses_correct_template(self):
        self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('pool-test-environment:my-pool-environments'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my-pool-environments-test.html')