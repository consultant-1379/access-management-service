from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse, reverse_lazy
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PoolTestEnvironment.models import *
from PoolTestEnvironment.serializers import *
from .tables import *
from .filters import NamespaceFilter
from django_tables2 import SingleTableView
from django.http import JsonResponse,HttpResponseRedirect
from django.views import View
import json
from jenkinsapi.jenkins import Jenkins
from PoolTestEnvironment.constants import values
from django.utils import timezone
from datetime import timedelta
import requests
from django.db.models import Q
from .forms import PartialBookingForm, BookingForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib import messages
from jira import JIRA, JIRAError
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django_tables2 import RequestConfig
from django.views.generic.edit import UpdateView
from .jira_helper import booking_details_comment
# from django.contrib.auth.decorators import login_required

# Api Views
class BookingList(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class NamespaceList(generics.ListAPIView):
    queryset = Namespace.objects.all()
    serializer_class = NamespaceSerializer

class BookingAPIView(APIView):
    def get_queryset(self):
        return Booking.objects.all()
    


    def get(self, request, namespace=None, format=None):
        try:
            ns = Namespace.objects.get(name=namespace)
        except Namespace.DoesNotExist:
            return Response({"detail": "No namespace found with this name."}, status=status.HTTP_404_NOT_FOUND)

        try:
            booking = Booking.objects.get(namespace=ns)
            serializer = BookingSerializer(booking)
            return Response(serializer.data)
        except Booking.DoesNotExist:
            return Response({"detail": "No booking found with this namespace."}, status=status.HTTP_404_NOT_FOUND)
        


    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, namespace=None):
        try:
            ns = Namespace.objects.get(name=namespace)
        except Namespace.DoesNotExist:
            return Response({"detail": "No namespace found with this name."}, status=status.HTTP_404_NOT_FOUND)

        try:
            booking = Booking.objects.get(namespace=ns)
        except Booking.DoesNotExist:
            return Response({"detail": "No booking found with this namespace."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookingCreateSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, namespace=None):
        try:
            ns = Namespace.objects.get(name=namespace)
        except Namespace.DoesNotExist:
            return Response({"detail": "No namespace found with this name."}, status=status.HTTP_404_NOT_FOUND)

        try:
            booking = Booking.objects.get(namespace=ns)
        except Booking.DoesNotExist:
            return Response({"detail": "No booking found with this namespace."}, status=status.HTTP_404_NOT_FOUND)

        booking.delete()
        return Response({"detail": "Booking deleted."}, status=status.HTTP_204_NO_CONTENT)


# Table Views
class NamespaceTableView(SingleTableView):
    model = Namespace
    table_class = NamespaceTable
    template_name = 'pool-data.html'
    # table_pagination = {"per_page": 50}
    SingleTableView.table_pagination = False

    def get_table_data(self):
        data = super().get_table_data()
        self.filter = NamespaceFilter(self.request.GET, queryset=data)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

def get_suitable_namespaces(requested_cpu, requested_memory):
    return Namespace.objects.filter(cluster__cpu_available__gte=requested_cpu, cluster__memory_available__gte=requested_memory)



# Table Views
class BookingRequestsTableView(SingleTableView):
    model = Booking
    table_class = BookingRequestsTable
    template_name = 'booking-requests.html'
    # table_pagination = {"per_page": 20}
    SingleTableView.table_pagination = False

    def get_queryset(self):
        return Booking.objects.filter(namespace__isnull=True)
    
# Table Views
class MyPoolEnvironmentsTableView(SingleTableView):
    model = Namespace
    table_class = MyPoolEnvironmentsTable     #NamespaceTable
    template_name = 'my-pool-environments.html'
    SingleTableView.table_pagination = False

    def get_queryset(self):
        username = self.request.user.username
        print('Logged in user is: ',self.request.user.username)
        
        # # Test With Random user - Uncomment to test for a specific id
        # username = 'eforgav'
        return super().get_queryset().filter(booking__team__users__contains=[username])

# My Pool Environment View with 2 tables (Active bookings & Opening requests)
class MyPoolEnvironmentsView(TemplateView):
    template_name = 'my-pool-environments-test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.user.username

        # Uncomment to test with different users
        # username = 'zyapdum'
        

        users_pool_environments = Namespace.objects.filter(booking__team__users__contains=[username])
        users_pool_environment_requests = Booking.objects.filter(Q(team__users__contains=[username]) & Q(namespace__isnull=True)) #  namespace__isnull=True, booking__team__users__contains=[username]

        table1 = MyPoolEnvironmentsTable(users_pool_environments)
        # table2 = BookingRequestsTable(users_pool_environment_requests)
        table2 = MyBookingRequestsTable(users_pool_environment_requests)

        RequestConfig(self.request).configure(table1)
        RequestConfig(self.request).configure(table2)

        context['table1'] = table1
        context['table2'] = table2

        return context

class RequestEnvironmentView(LoginRequiredMixin,FormView):
    form_class = PartialBookingForm

    def get_initial(self):
        today = timezone.now()
        end_date = (timezone.now() + timedelta(weeks=2))
        initial = super().get_initial()
        initial['booking_start_date'] = today
        initial['booking_end_date'] = end_date
        initial['tls_enabled'] = False
        return initial

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        return render(request, 'request-pool-environment.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        jira_id = form.cleaned_data['jira_id']
        team = form.cleaned_data['team']
        app_set = form.cleaned_data['app_set']
        today = (form.cleaned_data['booking_start_date']).strftime('%Y-%m-%d')
        end_date = (form.cleaned_data['booking_end_date']).strftime('%Y-%m-%d')
        tls_enabled = str(form.cleaned_data['tls_enabled'])
        jira_comment = (form.cleaned_data['jira_comment'])
        if self.request.user.username ==  "admin":
            reporter = 'eforgav'
        else:
            print(f"Logged in user is: {self.request.user.username}")
            reporter = self.request.user.username
         
        print("Jira id is: ",jira_id)
        if not jira_id:
            print("JIRA ID is None or an empty string")
            try:
                jira = JIRA(server=values.JIRA_URL, token_auth = values.JIRA_PAT_TOKEN) # Get Jira client
                fields = {
                    'project': {'key': 'DETS'},  
                    'summary': f'Team {team} Booking Ticket Request for AMS - Pool Test',
                    'customfield_11911': 'DETS-27474', # Epic Link
                    'description': f'App set is {app_set}. TLS Enabled - {tls_enabled}',
                    'issuetype': {'name': 'Task'},
                    # 'assignee': {'name': 'eforgav'}, 
                    # 'environment':  'Hart173-eric-eic-5',
                    'labels': ['EIAP_Pooled_Deployments'],
                    'components':[{'name': 'idun_aas'},{'name': 'team muon'}],
                    'reporter': {'name': reporter}, # Change to self.request.user.username 
                    'customfield_19947': today, # Planned start Date
                    'customfield_19946': end_date, # Planned End Date
                    # 'customfield_25604:': {'value': 'Shared'}, # Access Solution
                    'priority': {'name': 'Minor'}, 
                    'customfield_20067': [{'value': 'Testing'}], # Type
                    # 'customfield_35101': [{'value': 'dmm-e2e-cicd'}], # Installation Type
                }
                print(fields)
                issue = jira.create_issue(fields)
                print("New created jira is ",issue.key)
                print(f'Jira comment is : {jira_comment}')

                try:
                    # Add comment if its not empty
                    if jira_comment:
                        jira.add_comment(issue,jira_comment)
                except Exception as e:
                    print(f"An error occured: {e}")

                instance = form.save(commit=False)
                instance.jira_id = issue.key
                instance.save()
                messages.success(self.request, mark_safe(f'Your environment request has been successfully submitted. Please follow this jira for updates - <a href="{values.JIRA_URL}/browse/{issue.key}">{issue.key}</a>.'))
            except Exception as e:
                print(f"An error occured: {e}")
                messages.error(request, 'Error creating Ticket & Request.')
        else:
            print("JIRA ID is not None or an empty string")
            form.save()
            messages.success(self.request, mark_safe(f'Your environment request has been successfully submitted. Please follow this jira for updates - <a href="{values.JIRA_URL}/browse/{issue.key}">{issue.key}</a>.'))
        
        return redirect('/pool-deployments/my-environments/')  

    def form_invalid(self, form):
        return render(request, 'template_name.html', {'form': form})

class TriggerJenkinsView(View):

    def trigger_jenkins_job(self,job_name,build_params):
        server = Jenkins(values.JENKINS_URL,username=values.JENKINS_USERNAME,password=values.JENKINS_TOKEN,ssl_verify=False)
        job = server[job_name]
        queue_item = job.invoke(build_params=build_params)

        if queue_item.is_queued() or queue_item.is_running():
            return {"status": "Build triggered successfully"}
        else:
            return {"status": "Failed to trigger build"}

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        namespace_id = data.get('namespace_id')
        print("Namespace id is: ", namespace_id)
        namespace_name = data.get('name')
        print(namespace_name)
        action = data.get('action')
        cluster_name = namespace_name.split("-")[0]
        namespace_number = namespace_name.split("-")[-1]
        print("Namespace number is: {}".format(namespace_number))
        kubeconfig = cluster_name  + '_kubeconfig'
        print(action)

        if action == 'edit-booking':
            print(f'Edit booking assigned to namespace {namespace_name}')
            try:
                booking = Booking.objects.get(namespace=namespace_id)
                print(f'Booking id is {booking.id}, and team is {booking.team.name}')
            except Booking.DoesNotExist:
                print("detail: No booking found with this namespace.")
            
            return JsonResponse({'status': 'redirect', 'redirect_url': f'/pool-deployments/booking/update/{booking.id}/'})
            
            
        
        # Trigger Teardown
        if action == 'trigger-teardown':
            build_parameters = {
                'NAMESPACE': namespace_name,
                'CRD_NAMESPACE': values.CRD_NAMESPACE,
                'KUBECONFIG_FILE': kubeconfig,
                'REMOVE_BOOKED_ANNOTATION':'true'
            }
            print(values.JENKINS_URL)
            response = self.trigger_jenkins_job(job_name=values.TEARDOWN_JOB,build_params=build_parameters)
            return JsonResponse(response)

        # Trigger Re-install
        elif action == 'trigger-reinstall':
            try:
                booking = Booking.objects.get(namespace=namespace_id)
            except Booking.DoesNotExist:
                print("detail: No booking found with this namespace.")

            build_parameters = {
                'CLUSTER_NAME': cluster_name,
                'NAMESPACE_NUMBER': namespace_number,
                'EIC_VERSION': '0.0.0',
                'GENERATE_HTTPS_CERTS': 'true',
                'TEAM_NAME': booking.team.name,
                'TAGS': booking.app_set,
                'ENABLE_TLS': str(booking.tls_enabled)
            }
            print(build_parameters)
            # response = {'status': 'Test'}
            response = self.trigger_jenkins_job(job_name=values.EIC_EASY_TRIGGER_JOB,build_params=build_parameters)
            return JsonResponse(response)
        
        # Booking Extension
        elif action == 'extend-booking':
            today = timezone.now().strftime('%d-%m-%Y')
            # extension_date = (timezone.now() + timedelta(weeks=2)).strftime('%d-%m-%Y')
            try:
                booking = Booking.objects.get(namespace=namespace_id)
            except Booking.DoesNotExist:
                print("detail: No booking found with this namespace.")
            
            if booking.booking_end_date > timezone.now().date():
                print("End date is greater than today extending 2 weeks from end date")
                extension_date = (booking.booking_end_date + timedelta(weeks=2)).strftime('%d-%m-%Y')
                print(extension_date)
            else:
                extension_date = (timezone.now() + timedelta(weeks=2)).strftime('%d-%m-%Y')
                
            users = ','.join(list(booking.team.users))
            print(users)
            build_parameters = {
                'ACTION': 'add',
                'BOOKED_FOR': users,
                'NAMESPACE': namespace_name,
                'JIRA_ID': booking.jira_id,
                'EIC_VERSION': booking.eic_version,
                'APP_SET': booking.app_set,
                'START_DATE': today,
                'END_DATE': extension_date,
                'KUBECONFIG_FILE': kubeconfig,
                'TEAM_NAME': booking.team.name
            }
            print(build_parameters)
            # response = {'status': 'Test'}
            response = self.trigger_jenkins_job(job_name=values.MANAGE_BOOKINGS_JOB,build_params=build_parameters)
            return JsonResponse(response)
        
        # Trigger Automation
        elif action == 'trigger-automation':
            print(f'Edit booking with id {namespace_id}') # Namespace id is booking id
            try:
                booking = Booking.objects.get(id=namespace_id)
                print(f'Booking id is {booking.id}, and team is {booking.team.name}')
                print(f'Booking appset is {booking.app_set}')
            except Booking.DoesNotExist:
                print("detail: No booking found with this id.")
            
            return JsonResponse({'status': 'redirect', 'redirect_url': f'/pool-deployments/booking-requests/update/{booking.id}/'})

        # Trigger reject booking or delete booking request
        elif action == 'reject-booking' or action == 'delete-request':
            try:
                booking = Booking.objects.get(id=namespace_id) # In this case namespace_id is actually the booking id
                print(f"booking team is {booking.team}, app set: {booking.app_set},Jira is: {booking.jira_id}")
                booking.delete()
            
            except Booking.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Booking not found'}, status=404)

            try:
                # Comment on Jira and move to closed state
                print("Entering Jira commands now! Changing state and making comment")
                transition_to = "Closed"
                jira = JIRA(server=values.JIRA_URL, token_auth = values.JIRA_PAT_TOKEN) # Get Jira client
                issue = jira.issue(booking.jira_id)
                if action == 'reject-booking':
                    jira.add_comment(issue,'Booking has been rejected by AMS Automation Portal. This likely means your team already has too many environments.')
                elif action == 'delete-request':
                    jira.add_comment(issue,'User no longer needs the environment and has cancelled the booking request. ')
                
                valid_transitions = jira.transitions(issue)
                # print(valid_transitions)
                closed_transition_id = [t['id'] for t in valid_transitions if t['name'].lower() == 'closed'][0]
                jira.transition_issue(issue,closed_transition_id)
                return JsonResponse({'status': 'success'})

            except JIRAError as e:
                return JsonResponse({'An Error has Occured with JIRA:': str(e)}, status=400)
                print(f"An Error has Occured with JIRA: {e.text}")

        # Delete booking from the namespace
        elif action == 'terminate-booking':
            try:
                booking = Booking.objects.get(namespace=namespace_id) 
                print(f"booking team is {booking.team}, app set: {booking.app_set},Jira is: {booking.jira_id}")
                booking.delete()
            
            except Booking.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Booking not found'}, status=404)

            try:
                # Comment on Jira and move to closed state
                print("Entering Jira commands now! Changing state and making comment")
                transition_to = "Closed"
                jira = JIRA(server=values.JIRA_URL, token_auth = values.JIRA_PAT_TOKEN) # Get Jira client
                issue = jira.issue(booking.jira_id)
                jira.add_comment(issue,'User no longer needs the environment and has cancelled the booking request. ')
                
                valid_transitions = jira.transitions(issue)
                # print(valid_transitions)
                closed_transition_id = [t['id'] for t in valid_transitions if t['name'].lower() == 'closed'][0]
                jira.transition_issue(issue,closed_transition_id)
                return JsonResponse({'status': 'success'})

            except JIRAError as e:
                return JsonResponse({'An Error has Occured with JIRA:': str(e)}, status=400)
                print(f"An Error has Occured with JIRA: {e.text}")

        elif action == 'request-support':
            try:
                message = "Support feature not available in this release. Coming soon!"
                messages.info(request,message)
                print(message)
                # return HttpResponseRedirect(reverse('pool-test-environment:my-pool-environments'))
                return JsonResponse({'status': 'success'})

            except Exception as e:
                return HttpResponseRedirect(reverse('pool-test-environment:my-pool-environments'))
                # JsonResponse({'status': 'error', 'message': 'error'}, status=500)
        
        # Booking details Comment
        elif action == 'comment-details':
            try:
                booking = Booking.objects.get(namespace=namespace_id)
            except Booking.DoesNotExist:
                print("detail: No booking found with this namespace.")
            
            # users = ','.join(list(booking.team.users))
            # print(users)
            jira = JIRA(server=values.JIRA_URL, token_auth = values.JIRA_PAT_TOKEN) # Get Jira client
            issue = jira.issue(booking.jira_id)
            fqdn = booking.fqdn
            reporter = issue.fields.reporter.name

            # Make Jira Comment with booking details
            comment = booking_details_comment(
                jira_id = booking.jira_id,
                team = booking.team.name,
                pm = booking.team.project_manager,
                start_date = booking.booking_start_date,
                end_date = booking.booking_end_date,
                cluster_name = booking.namespace.cluster.name,
                namespace = booking.namespace.name,
                fqdn = booking.namespace.fqdn,
                eic_version = booking.eic_version,
                reporter = reporter,
                ip = booking.namespace.ip
            )

            try:
                jira.add_comment(issue,comment)
            except Exception as e:
                print(f"An error occured: {e}")

            return JsonResponse({'status': 'Success: Comment successful'})

        else: 
            return JsonResponse({'status': 'Error: No jenkins job endpoint defined for {}'.format(action)})
        
        

class BookingUpdateView(UpdateView):
    team = forms.ModelChoiceField(queryset=Team.objects.all())
    booking_start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    booking_end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    # tls_enabled = forms.BooleanField(help_text='Check this box if want TLS Enabled.')
    tls_enabled = forms.ChoiceField(
        choices=[(True, 'True'), (False, 'False')],
        widget=forms.Select,
        initial=False,
    )
    model = Booking
    fields = '__all__'  
    template_name = 'pool-booking-update.html'
    success_url = reverse_lazy('pool-test-environment:pool-data')  

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class.base_fields['tls_enabled'] = forms.ChoiceField(
        choices=[(True, 'True'), (False, 'False')],
        widget=forms.Select,
        initial=False,
        )
        return form_class      

class AssignNamespaceToBookingView(UpdateView):
    model = Booking
    fields = '__all__'  
    template_name = 'assign-namespace-to-booking.html'  
    success_url = reverse_lazy('pool-test-environment:pool-data')

    def get_form_class(self):
        form_class = super().get_form_class()

        cpu_required, memory_required = self.object.calculate_requirements()

        form_class.base_fields['namespace'] = forms.ModelChoiceField(
        queryset=Namespace.objects.filter(cluster__cpu_available__gte=cpu_required, cluster__memory_available__gte=memory_required).exclude(booking__isnull=False)
        )

        # Adjust the other fields
        form_class.base_fields['team'] = forms.ModelChoiceField(queryset=Team.objects.all())
        form_class.base_fields['booking_start_date'] = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
        form_class.base_fields['booking_end_date'] = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
        form_class.base_fields['tls_enabled'] = forms.ChoiceField(
            choices=[(True, 'True'), (False, 'False')],
            widget=forms.Select,
            initial=False,
        )
        
        return form_class

        