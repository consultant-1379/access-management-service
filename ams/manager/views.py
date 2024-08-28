from django.shortcuts import render, redirect, get_object_or_404
import django_tables2 as tables
from django.core.mail import send_mail
from django.db.models import Q
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import RequestConfig
from .models import *
from .tables import *
from .filters import *
from django.contrib.auth.decorators import login_required
from .forms import *
from datetime import datetime
from formtools.wizard.views import SessionWizardView
from django.http import HttpResponseRedirect
from .enmconmgr import *
from django.db.models import ProtectedError
from externalfeeds.getters import *
from externalfeeds.jira_helper import  *
from django.contrib.auth.models import Group
from .restriction import *
from django.urls import reverse_lazy
from .helpers import *
from django.conf import settings


logger = logging.getLogger(__name__)

def access_denied(request):
    return render(request, 'access_denied.html')

def jira_failed(request):
    return render(request, 'jira_failed.html')

# Class views for wizzard.

class AddOrderView(LoginRequiredMixin, SessionWizardView):
    template_name = 'account-order.page.tmpl.html'
    form_list = [OrderAccountStepOne, OrderAccountStepTwo,OrderAccountStepThree,OrderAccountStepFour] 
    notes =""

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        
        if step is None:
            step = self.steps.current

        # Customize StepTwoForm queryset based on selection in StepOneForm
        if step == '1':
            form_area = self.get_cleaned_data_for_step('0')['area']
            form_type = self.get_cleaned_data_for_step('0')['system_type']
            form_is_functional_user = self.get_cleaned_data_for_step('0')['is_functional_user']           
           
            current_user = AMSUser.objects.get(username=self.request.user.username)

            form.fields['user'] = forms.ModelChoiceField(label='Account owner',queryset=AMSUser.objects.all().order_by('username'), widget=forms.Select(attrs={'class': 'select'}),initial=current_user.id)

            if form_is_functional_user == 'False' :
                form.fields['account_name'] = forms.CharField(widget=forms.HiddenInput, initial="none", label='Hidden Field')
            if "ENM" in str(form_type):
                form.fields['account_profile'] = forms.ModelChoiceField(label='Account profile',queryset=ENMUserProfile.objects.filter(Q(name='BASIC')|Q(name='SECURITY')|Q(name='XFTTEST')|Q(name='PICOAI')), widget=forms.Select(attrs={'class': 'select'}))
            elif "EIC" in str(form_type) or "PTEaaS" in str(form_type):
                form.fields['account_profile'] = forms.ModelChoiceField(label='Account profile',queryset=EICUserProfile.objects.all(), widget=forms.Select(attrs={'class': 'select'}))
            elif "EO" in str(form_type):
                form.fields['account_profile'] = forms.ModelChoiceField(label='Account profile',queryset=EOUserProfile.objects.all(), widget=forms.Select(attrs={'class': 'select'}))
            else:
                form.fields['account_profile'] = forms.ModelChoiceField(label='Account profile',queryset=ENMUserProfile.objects.none())

        if step == '2':
            step0_data = self.get_cleaned_data_for_step('0')
            step1_data = self.get_cleaned_data_for_step('1')
            form_area = step0_data['area']
            form_type = step0_data['system_type']
            if step0_data['is_functional_user'] == 'False':
                account = step1_data['user']
            else:
                account = step1_data['account_name']
            try:
                ams_account = Account.objects.get(name=account)
                system_list = list(ams_account.systems.values_list('pk', flat=True))
            except Account.DoesNotExist:
                system_list = []

            form.fields['systems'].queryset = System.objects.filter(area_id=form_area, type_id=form_type,is_active=True).exclude(pk__in=system_list)
            form.fields['systems'].initial = []
    
        if step == '3':
            step0_data = self.get_cleaned_data_for_step('0')
            step1_data = self.get_cleaned_data_for_step('1')
            step2_data = self.get_cleaned_data_for_step('2')
            if step0_data['is_functional_user'] == 'False':
                account = step1_data['user']
            else:
                account = step1_data['account_name']
            systems = step2_data['systems']
            systems_names = [system.name for system in systems]
            form.initial['summary']=f"Order for: {step1_data['user']}\nAccount: {account}\nUser Profile: {step1_data['account_profile']}\nArea: {step0_data['area']}\nSystem Type: {step0_data['system_type']}\nSystems : {systems_names}"
            

        return form

    def get_context_data(self,form, **kwargs):
        context = super().get_context_data(form=form,**kwargs)
        context['title1'] = 'Account'
        context['subtitle1'] = 'Order New'
        context['profileTable'] = ENMProfileTableShort([])

        if self.steps.current == '0':
            context['notes'] =  format_html('Choosing functional user will alow to specify username.<br> Other case only account with signum can be created.<br><b>NOTE:<br>for creatng real user account please leave functionl user set to NO</b>')
            context['left'] =  format_html('<h3>Please choose:</h3>')
        elif self.steps.current == '1':
            form_type = self.get_cleaned_data_for_step('0')['system_type']
            context['notes'] = format_html('Please choose at account settings. <br> If you are ordering for real user its signum will be used')
            context['left'] =  format_html('<h3>Please choose:</h3>')

            if "ENM" in str(form_type):
                profile_list = ENMUserProfile.objects.filter(Q(name='BASIC')|Q(name='SECURITY')|Q(name='XFTTEST')|Q(name='PICOAI'))
                profileTable = ENMProfileTableShort(profile_list)
                context['profileTable'] = profileTable

        elif self.steps.current == '2':
            step0_data = self.get_cleaned_data_for_step('0')
            step1_data = self.get_cleaned_data_for_step('1')
            context['notes'] = format_html('Please choose at least one system. <br>')
            context['left'] =  format_html('<h3>Please choose:</h3>')
            context.update({
                'step0_data': step0_data,
                'step1_data': step1_data,
            })

        elif self.steps.current == '3':
            step0_data = self.get_cleaned_data_for_step('0')
            step1_data = self.get_cleaned_data_for_step('1')
            step2_data = self.get_cleaned_data_for_step('2')
            context['notes'] = format_html('If all data is correct please click submit' + "<br><b>NOTE:<br> After your account is accepted</b><br>please visit: " +"<a href="+ reverse('manager:my_profile') +"> My profile</a> and reset your password for your system account")
            context['left'] =  format_html('<h3>Please review:</h3>')
            context.update({
                'step0_data': step0_data,
                'step1_data': step1_data,
                'step2_data': step2_data,
            })
        return context

    def done (self, form_list, **kwargs):
        added_items = []  # Initialize an empty list to store deleted item IDs
        failed_to_add_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted
        step0_data = self.get_cleaned_data_for_step('0')
        step1_data = self.get_cleaned_data_for_step('1')
        step2_data = self.get_cleaned_data_for_step('2')
        systems = step2_data['systems']
        system_type = step0_data['system_type']
        area = step0_data['area']
        systems_names = [system.name for system in systems]
        account_profile = step1_data['account_profile']
        if step0_data['is_functional_user'] == 'False':
            account_name = step1_data['user'].username
        else:
            account_name = step1_data['account_name']
        ## CREATE ACCOUNT OBJECT IF DOES NOT EXISTS
        try:
            account =  Account.objects.get(name = account_name)
        except Account.DoesNotExist:
            account = None 

        if account == None :
            logger.info("creating account: " + account_name)
            account = Account(
            name = account_name,
            user = step1_data['user'],
            is_active = False,
            is_functional_user = step0_data['is_functional_user'],
            )
        account.save()
        account.systems.add(*step2_data['systems'])
        account.save()

        desc = "AMS ticket for: " + step1_data['user'].username + ". Account: " + account_name + " on systems: " + str(systems_names) + " with profile: " + str(account_profile)
        
        specific_area = Area.objects.get(name=area)  
            # Retrieve the related Approvers for the specific area
        approvers_for_area = Approver.objects.filter(area=specific_area)

            # Create a list of usernames associated with the Approvers
        usernames_for_area = [approver.user.username for approver in approvers_for_area]



        jira_number = createJira(desc,area, self.request.user.username, approvers=usernames_for_area )

        if "Failed" not in  jira_number:
            jira = JiraTicket(
                account = account,
                description = desc,
                ticket_number = jira_number
            )
            jira.save()
            logger.info("JIRA ticket Object created " + jira_number)
        else:
            logger.warning("JIRA ticket cration failed failed please see externalfeeds log")
            return HttpResponseRedirect(reverse('manager:jira_failed'))


        order_placed = 0 
        ## CREATE ORDER SYSTEN USERS and approvals
        for system in systems:
            ## CREATE ORDER OBJECT
    
            order = Order(
                account = account,
                jira_ticket = jira,
                system = system,
                ordered_by = self.request.user
            )
            
            try:
                if "ENM" in str(system_type):

                    if not ENMUser.objects.filter( system = system, account = account).exists() :

                        system_account = ENMUser(
                            account = account,
                            profile = account_profile, 
                            system = system,
                        )
                        system_account.save() 
                        order.save()
                        added_items.append({'name': account_name, 'system': system.name})
                        order_placed =  order_placed +1
                    else:
                        commentJira(jira_number,"Account " + account_name + " on system "+ system.name +" already exists")
                        logger.warning(jira_number + " Account " + account_name + " on system "+ system.name +" already exists")
                        raise Exception("Account already exists")

                elif "EIC" in str(system_type):
                    if not EICUser.objects.filter( system = system, account = account).exists() :

                        system_account = EICUser(
                            account = account,
                            profile = account_profile, 
                            system = system,
                        )
                        system_account.save() 
                        order.save()
                        added_items.append({'name': account_name, 'system': system.name})
                        order_placed =  order_placed +1
                    else:
                        commentJira(jira_number,"Account " + account_name + " on system "+ system.name +" already exists")
                        logger.warning(jira_number + " Account " + account_name + " on system "+ system.name +" already exists")
                        raise Exception("Account already exists")

                elif "EO" in str(system_type):
                    if not EOUser.objects.filter( system = system, account = account).exists() :

                        system_account = EOUser(
                            account = account,
                            profile = account_profile, 
                            system = system,
                        )
                        system_account.save() 
                        order.save()
                        added_items.append({'name': account_name, 'system': system.name})
                        order_placed =  order_placed +1
                    else:
                        commentJira(jira_number,"Account " + account_name + " on system "+ system.name +" already exists")
                        logger.warning(jira_number + " Account " + account_name + " on system "+ system.name +" already exists")
                        raise Exception("Account already exists")
            except Exception as e:
                failed_to_add_items.append({'name': account.name, 'system': system.name, "error": e}) 
            
            if order_placed == 0 :
                close_jira(jira_number)

        return render(self.request, "add-order-summary.page.tmpl.html",{
            "title1": 'Orders creation',
            "subtitle1": "Summary",
            "added_items":added_items,
            "failed_to_add_items":failed_to_add_items,
        })
    
## CREATE ACCOUNT WIZZARD
class AddAccountView(LoginRequiredMixin, SessionWizardView):
    template_name = 'account-add-wizz.page.tmpl.html'
    form_list = [OrderAccountStepOne, OrderAccountStepTwo,OrderAccountStepThree,OrderAccountStepFour] 
    notes =""

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current

        # Customize StepTwoForm queryset based on selection in StepOneForm
        if step == '1':
            form_area = self.get_cleaned_data_for_step('0')['area']
            form_type = self.get_cleaned_data_for_step('0')['system_type']
            form_is_functional_user = self.get_cleaned_data_for_step('0')['is_functional_user']

            current_user = AMSUser.objects.get(username=self.request.user.username)

            form.fields['user'] = forms.ModelChoiceField(label='Account owner',queryset=AMSUser.objects.all().order_by('username'), widget=forms.Select(attrs={'class': 'select'}),initial=current_user.id)
            
            if form_is_functional_user == 'False' :
                form.fields['account_name'] = forms.CharField(widget=forms.HiddenInput, initial="none", label='Hidden Field')

            if "ENM" in str(form_type):
                form.fields['account_profile'] = forms.ModelChoiceField(label='Account profile',queryset=ENMUserProfile.objects.all(), widget=forms.Select(attrs={'class': 'select'}))
            elif "EIC" in str(form_type):
                form.fields['account_profile'] = forms.ModelChoiceField(label='Account profile',queryset=EICUserProfile.objects.all(), widget=forms.Select(attrs={'class': 'select'}))
            elif "EO" in str(form_type):
                form.fields['account_profile'] = forms.ModelChoiceField(label='Account profile',queryset=EOUserProfile.objects.all(), widget=forms.Select(attrs={'class': 'select'}))
        
           

        if step == '2':
            step0_data = self.get_cleaned_data_for_step('0')
            step1_data = self.get_cleaned_data_for_step('1')
            form_area = step0_data['area']
            form_type = step0_data['system_type']
            if step0_data['is_functional_user'] == 'False':
                account = step1_data['user']
            else:
                account = step1_data['account_name']
            try:
                ams_account = Account.objects.get(name=account)
                system_list = list(ams_account.systems.values_list('pk', flat=True))
            except Account.DoesNotExist:
                system_list = []

            form.fields['systems'].queryset = System.objects.filter(area_id=form_area, type_id=form_type,is_active=True).exclude(pk__in=system_list)
            form.fields['systems'].initial = []
    
        if step == '3':
            
            step0_data = self.get_cleaned_data_for_step('0')
            step1_data = self.get_cleaned_data_for_step('1')
            step2_data = self.get_cleaned_data_for_step('2')
            if step0_data['is_functional_user'] == 'False':
                account = step1_data['user']
            else:
                account = step1_data['account_name']
            systems = step2_data['systems']
            systems_names = [system.name for system in systems]
            form.initial['summary']=f"Order for: {step1_data['user']}\nAccount: {account}\nUser Profile: {step1_data['account_profile']}\nArea: {step0_data['area']}\nSystem Type: {step0_data['system_type']}\nSystems : {systems_names}"
            
  
        return form

    def get_context_data(self,form, **kwargs):
        context = super().get_context_data(form=form,**kwargs)
        context['title1'] = 'Account'
        context['subtitle1'] = 'Add New'

        if self.steps.current == '0':
            context['notes'] =  format_html('Choosing functional user will alow to specify username.<br> Other case only account with signum can be created.<br><b>NOTE:<br>for creatng real user account please leave functionl user set to NO</b>')
            context['left'] =  format_html('<h3>Please choose:</h3>')
        elif self.steps.current == '1':
            context['notes'] = format_html('Please provide user details.<br> If you are ordering for real user its signum will be used')
            context['left'] =  format_html('<h3>Please choose:</h3>')
        elif self.steps.current == '2':
            context['notes'] = format_html('Please choose at least one system')
            context['left'] =  format_html('<h3>Please choose:</h3>')
        elif self.steps.current == '3':
            step0_data = self.get_cleaned_data_for_step('0')
            step1_data = self.get_cleaned_data_for_step('1')
            step2_data = self.get_cleaned_data_for_step('2')
            context['notes'] = format_html('If all data is correct please click submit')
            context['left'] =  format_html('<h3>Please review:</h3>')
            context.update({
                'step0_data': step0_data,
                'step1_data': step1_data,
                'step2_data': step2_data,
            })
        return context

    def done (self, form_list, **kwargs):
        added_items = []  # Initialize an empty list to store deleted item IDs
        failed_to_add_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted
        step0_data = self.get_cleaned_data_for_step('0')
        step1_data = self.get_cleaned_data_for_step('1')
        step2_data = self.get_cleaned_data_for_step('2')
        systems = step2_data['systems']
        system_type = step0_data['system_type']
        current_user = self.request.user
        account_profile = step1_data['account_profile']
        if step0_data['is_functional_user'] == 'False':
            account_name = step1_data['user'].username
        else:
            account_name = step1_data['account_name']
        ## CREATE ACCOUNT OBJECT IF DOES NOT EXISTS
        try:
            account =  Account.objects.get(name = account_name)
        except Account.DoesNotExist:
            account = None 

        if account == None :
            logger.info("Creating Account " + account_name)
            account = Account(
            name = account_name,
            user = step1_data['user'],
            is_functional_user = step0_data['is_functional_user'],
            )
        account.save()
        account.systems.add(*step2_data['systems'])
        account.save()


        for system in systems:
            try:
                if "ENM" in str(system_type):

                    if not ENMUser.objects.filter( system = system, account = account).exists() :

                        system_account = ENMUser(
                            account = account,
                            profile = account_profile, 
                            system = system,
                            is_approved = True,
                            # aproved_by = current_user, ## need to find a better way to set who approved account
                        )
                        if check_enmuser(account_name, system) != 0:
                            new_enm_account = create_enm_account(account_name, system, account_profile)
                        else:
                            new_enm_account = 1
                        
                        if new_enm_account == 1:
                            system_account.save()
                            added_items.append({'name': account_name, 'system': system.name})
                            logger.info("Account "+ account_name + " on system" + system.name + " created")
                        elif new_enm_account == 22:
                            logger.error("Can't establish session towards ENM: " + system.name)
                            raise Exception("Can't establish session towards ENM.")
                        elif new_enm_account == 27:
                            logger.error("Admin user and password not set for system: " + system.name)
                            raise Exception("Admin user and password not set for system.")
                        else:
                            logger.error(("ENM account not created: " + account_name + " on system " + system.name))
                            raise Exception("ENM account not created.")
                    else:
                        logger.warning(" Account " + account_name + " on system "+ system.name +" already exists")
                        raise Exception("Account already exists")

                elif "EIC" in str(system_type):
                    system_account = EICUser(
                        account = account,
                        profile = account_profile, 
                        system = system,
                        is_approved = True,
                        # aproved_by = current_user, ## need to find a better way to set who approved account 
                    )
                elif "EO" in str(system_type):
                    system_account = EOUser(
                        account = account,
                        profile = account_profile, 
                        system = system,
                        is_approved = True,
                        # aproved_by = current_user, ## need to find a better way to set who approved account
                    )   
            except Exception as e:
                failed_to_add_items.append({'name': account.name, 'system': system.name, "error": e})


        return render(self.request, "add-account-summary.page.tmpl.html",{
            "title1": 'Account creation',
            "subtitle1": "Summary",
            "added_items":added_items,
            "failed_to_add_items":failed_to_add_items,
        })
    

### MY PROFILE
@login_required
def my_profile(request):


    try:
        accounts = Account.objects.filter(user= request.user)
    except Account.DoesNotExist:
        accounts = None

    try:
        accountFilter = AccountFilter(request.GET, queryset=accounts)
        accountTable = AccountTable(accountFilter.qs)
        RequestConfig(request).configure(accountTable)
    except Account.DoesNotExist:
        accountTable = None    

    try:
        orderList = JiraTicket.objects.filter(account__user = request.user)
        orderFilter = JiraFilter(request.GET, queryset=orderList)
        orderTable = JiraTable(orderFilter.qs)
        RequestConfig(request).configure(orderTable)
    except JiraTicket.DoesNotExist:
        orderList = None  
        orderTable = None

    ### ENMUser accounts and profiles
    try:
        enmaccount = ENMUser.objects.filter(account__in= accounts, system__is_active = True)
    except ENMUser.DoesNotExist:
        enmaccount = None

    try:
        enmaccountFilter = ENMUserFilter(request.GET, queryset=enmaccount)
        enmaccountTable = ENMUserTable(enmaccountFilter.qs)
        RequestConfig(request).configure(enmaccountTable)
    except Approver.DoesNotExist:
        enmaccountFilter = None
        enmaccountTable = None 

    ### EOUser accounts and profiles
    try:
        eoaccount = EOUser.objects.filter(account__in= accounts, system__is_active = True)
    except EOUser.DoesNotExist:
        eoaccount = None

    try:
        eoaccountFilter = EOUserFilter(request.GET, queryset=eoaccount)
        eoaccountTable = EOUserTable(eoaccountFilter.qs)
        RequestConfig(request).configure(eoaccountTable)
    except Approver.DoesNotExist:
        eoaccountFilter = None
        eoaccountTable = None 

    ### EICUser accounts and profiles        
    try:
        eicaccount = EICUser.objects.filter(account__in= accounts, system__is_active = True)
    except EOUser.DoesNotExist:
        eoaccount = None

    try:
        eicaccountFilter = EICUserFilter(request.GET, queryset=eicaccount)
        eicaccountTable = EICUserTable(eicaccountFilter.qs)
        RequestConfig(request).configure(eicaccountTable)
    except Approver.DoesNotExist:
        eicaccountFilter = None
        eicaccountTable = None 
    ###

    title1= str(request.user.username)
    subtitle1 = "Details"

    return render(request, "my-account-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "accounts":accounts,
        "accountTable": accountTable,
        "accountFilter": accountFilter,
        "enmaccountTable" : enmaccountTable,
        "enmaccountFilter" : enmaccountFilter,
        "eoaccountTable" : eoaccountTable,
        "eoaccountFilter" : eoaccountFilter,
        "eicaccountTable" : eicaccountTable,
        "eicaccountFilter" : eicaccountFilter,
        "orderTable" : orderTable,
        "orderFilter" : orderFilter
    })


### ACCOUNTS 
@login_required
def account_list(request):
    try: 
        if request.user.is_operator or request.user.is_adminstrator:
            accountList = Account.objects.all()
        else:
            accountList = Account.objects.filter(user = request.user)   
        accountFilter = AccountFilter(request.GET, queryset=accountList)
        accountTable = AccountTable(accountFilter.qs)
        RequestConfig(request).configure(accountTable)
    except Account.DoesNotExist:
        accountList = None  
        accountTable = None

    title1= "Account"
    subtitle1 = "List"
  
    return render(request, "account-list.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "accountList": accountList,
        "accountTable": accountTable,
        "accountFilter": accountFilter,

    })

@login_required
def account_details(request, account_name):

    try:
        account = Account.objects.get(name=account_name)
    except Account.DoesNotExist:
        account = None  

    ### ENMUser accounts and profiles
    try:
        enmaccount = ENMUser.objects.filter(account = account, system__is_active = True)
    except ENMUser.DoesNotExist:
        enmaccount = None

    try:
        enmaccountFilter = ENMUserFilter(request.GET, queryset=enmaccount)
        enmaccountTable = ENMUserTable(enmaccountFilter.qs)
        RequestConfig(request).configure(enmaccountTable)
    except Approver.DoesNotExist:
        enmaccountFilter = None
        enmaccountTable = None 

    ### EOUser accounts and profiles
    try:
        eoaccount = EOUser.objects.filter(account = account, system__is_active = True)
    except EOUser.DoesNotExist:
        eoaccount = None

    try:
        eoaccountFilter = EOUserFilter(request.GET, queryset=eoaccount)
        eoaccountTable = EOUserTable(eoaccountFilter.qs)
        RequestConfig(request).configure(eoaccountTable)

    except Approver.DoesNotExist:
        eoaccountFilter = None
        eoaccountTable = None 

    ### EICUser accounts and profiles        
    try:
        eicaccount = EICUser.objects.filter(account = account, system__is_active = True)
    except EOUser.DoesNotExist:
        eoaccount = None

    try:
        eicaccountFilter = EICUserFilter(request.GET, queryset=eicaccount)
        eicaccountTable = EICUserTable(eicaccountFilter.qs)
        RequestConfig(request).configure(eicaccountTable)
    except Approver.DoesNotExist:
        eicaccountFilter = None
        eicaccountTable = None 
    ###



    try:
        systemList = account.systems.filter(is_active = True)
        systemFilter = SystemFilter(request.GET, queryset=systemList)
        systemTable = SystemTable(systemFilter.qs)
        RequestConfig(request).configure(systemTable)
    except Account.DoesNotExist:
        systemList = None  
        systemTable = None    

    title1= "Account"
    subtitle1 = "Details"

    return render(request, "account-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "account":account,
        "systemList": systemList,
        "systemTable": systemTable,
        "systemFilter": systemFilter,
        "enmaccountTable" : enmaccountTable,
        "enmaccountFilter" : enmaccountFilter,
        "eoaccountTable" : eoaccountTable,
        "eoaccountFilter" : eoaccountFilter,
        "eicaccountTable" : eicaccountTable,
        "eicaccountFilter" : eicaccountFilter
    })


############### SYSTEMS
@login_required
def system_list(request):
    try:
        
        systemList = System.objects.filter(is_active=True)
        systemFilter = SystemFilter(request.GET, queryset=systemList)
        systemTable = SystemTable(systemFilter.qs)
        RequestConfig(request, paginate={"per_page": 20}).configure(systemTable)
    except System.DoesNotExist:
        systemList = None  
        systemTable = None

    title1= "System"
    subtitle1 = "List"
  
    return render(request, "system-list.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "systemList": systemList,
        "systemTable": systemTable,
        "systemFilter": systemFilter

    })

@login_required
def system_status_set(request, system_name):
    if request.method == 'POST':
        try:
            system = System.objects.get(name=system_name)
        except System.DoesNotExist:
            system = System([]) 
        message = format_html(request.POST.get('message'))
        system.status = message
        system.save(update_fields=['status'])


    return redirect('manager:system_details', system_name=system_name)

def system_status_clear(request, system_name):
    if request.method == 'POST':
        try:
            system = System.objects.get(name=system_name)
        except System.DoesNotExist:
            system = System([]) 
        system.status = None
        system.save(update_fields=['status'])


    return redirect('manager:system_details', system_name=system_name)

@login_required
def system_email_send(request, system_name):
    emailList = []
    if request.method == 'POST':
        try:
            system = System.objects.get(name=system_name)
        except System.DoesNotExist:
            system = System([]) 

        try:
            accountList = Account.objects.filter(systems=system.id, is_active = True)
            emailList = [account.user.email for account in accountList]
        except Account.DoesNotExist:
            accountList = None  
        except Exception as e:
            logger.error("Errors getting emails: "  + str(e) )
            summary = "Errors getting emails: "  + str(e)

        title = "AMS notify for system: " + system.name + ": " + request.POST.get('title')  
        message = format_html(request.POST.get('message'))

        try:
            send_mail(title,'', settings.EMAIL_HOST_USER, emailList, html_message=message)
        except Exception as e:
            logger.error("Errors sending email: "  + str(e) )
            summary = "Errors sending emails: "  + str(e)
        summary ="E-mail send ok"

    return render(request, "system-email-send.page.tmpl.html",{
        "title1": "e-mail",
        "subtitle1": "send",
        "system": system,
        "emailList": ', '.join(emailList),
        "title": title,
        "message": message,
        "summary":summary,
    })

@login_required
def system_details(request, system_name):


    try:
        system = System.objects.get(name=system_name)
    except System.DoesNotExist:
        system = System([]) 

    try:
        accountList = Account.objects.filter(systems=system.id)
        accountFilter = AccountFilter(request.GET, queryset=accountList)
        accountTable = AccountTable(accountFilter.qs)
        RequestConfig(request).configure(accountTable)
    except Account.DoesNotExist:
        accountList = None  
        accountFilter =  AccountFilter()
        accountTable = AccountTable([])


    title1= "System"
    subtitle1 = "Details"
    title2 = "Other"
    monitoringLink = None
    title3 = "Other"
    title4 = "Remote accounts"
    ddpLink = None
    version = None
    doc2 = ""
    doc3 = ""
    doc4 = ""
    status=format_html('<span style="color:red" title="Cannot get connection info">FAILED</span>')

    dit_json = getters.getDeploymentFromDIT(system_name)

    dtt_json = getters.getDeploymentFromDTT(system_name)

    if "ENM" in str(system.type):
        ddpLink= getters.getDDPLinkFromFile(settings.DDP_LINKS_FILE, system_name)

    if str(system.type) == 'vENM':
        title2 = "VNF LCM SED"
        title3 = "SED"
        title4 = "ENM remote accounts"
        version = getters.getVenmVersionFromFile(settings.VENM_VERSION_FILE, system_name)
        monitoringLink = "https://monitoring1.stsoss.seli.gic.ericsson.se:3000/d/D00p3czKi/overall-vm-failures-consul-status-all-dc?orgId=1&var-dc=All&var-vpod=All&var-program=All&var-tenant=" + system_name
        try:
            doc2 = getters.getVnflcmSedFromDIT(system_name)['parameters']
            if doc2 == "none":
                raise Exception ("Document not found")
        except Exception as e:
            doc2 = dict(error=e)
            logger.error(" DIT VNF LCM System details: " + system_name + " with error: " + str(e)) 

        try:
            doc3 = getters.getSedFromDIT(system_name)['parameters']    
            if doc3 == "none":
                raise Exception ("Document not found")     
        except Exception as e:
            doc3 = dict(error=e)
            logger.error(" DIT SED System details: " + system_name + " with error: " + str(e)) 

        try:
            doc4 = list_enm_users(system_name)
        except Exception as e:
            doc4 = dict(error=e)
            logger.error(" ENM Users details: " + system_name + " with error: " + str(e)) 

    elif str(system.type) == 'cENM':
        title2 = "Deployment Values"
        title3 = "cENM SED"
        title4 = "ENM remote accounts"
        monitoringLink = "https://monitoring1.stsoss.seli.gic.ericsson.se:3000/d/ENM-statt-k8s/enm-k8s-dashboard?orgId=1&var-team=All&var-dc=All&var-vpod=All&var-program=All&var-cluster_id=" + system_name
        try:
            doc2 = getters.getCenmDeploymentValuesFromDIT(system_name)['parameters']
            if doc2 == "none":
                raise Exception ("Document not found")
        except Exception as e:
            doc2 = dict(error=e)
            logger.error(" DIT VNF LCM System details: " + system_name + " with error: " + str(e)) 

        try:
            doc3 = getters.getSedFromDIT(system_name)['parameters']    
            if doc3 == "none":
                raise Exception ("Document not found")     
        except Exception as e:
            doc3 = dict(error=e)
            logger.error(" DIT SED System details: " + system_name + " with error: " + str(e)) 

        try:
            doc4 = list_enm_users(system_name)
        except Exception as e:
            doc4 = dict(error=e)
            logger.error(" ENM Users details: " + system_name + " with error: " + str(e))
    

    elif str(system.type) == 'pENM':
        title2 = "pENM Document"
        title3 = "pENM SED"
        title4 = "ENM remote accounts"
        try:
            doc3 = getters.getSedFromDIT(system_name)['parameters']    
            if doc3 == "none":
                raise Exception ("Document not found")     
        except Exception as e:
            doc3 = dict(error=e)
            logger.error(" DIT SED System details: " + system_name + " with error: " + str(e))
        try:
            doc4 = list_enm_users(system_name)
        except Exception as e:
            doc4 = dict(error=e)
            logger.error(" ENM Users details: " + system_name + " with error: " + str(e))

    elif str(system.type) == 'EO':
        title2 = "Site Values"

    if dit_json != []:
        ditLink = "https://atvdit.athtem.eei.ericsson.se/deployments/view/"+ getters.getDeploymentIdFromDIT(dit_json)
    else:
        ditLink = None

    dtt_id = getters.getDeploymentIdFromDIT(dtt_json)
    if len(dtt_id) == 0:
        dttLink = None
    else:    
        dttLink = "https://atvdtt.athtem.eei.ericsson.se/deployments/view/"+ dtt_id
    
    hydra_ci_id = getters.getCiId(system_name)
    if len(hydra_ci_id) == 0:
        hydraLink = None
    else:
        hydraLink = "https://hydra.gic.ericsson.se/ci/"+ hydra_ci_id 

    if 'httpd_fqdn' in doc3:
        try:
            status = format_html('<span style="color:green" title="'+check_url_connectivity("https://"+doc3["httpd_fqdn"]+"/") + '">CONNECTED</span>')
        except Exception as e:
            status = format_html('<span style="color:red" title="'+str(e)+ '">FAILED</span>')
            logger.error("Cannot reach https://"+doc3["httpd_fqdn"]+"/with error: " + str(e))
    else:
        status = format_html('<span style="color:red" title="Cannot get httpd_fqdn">FAILED</span>')
    
  
    return render(request, "system-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "system": system,
        "title2": title2,
        "title3": title3,
        "title4": title4,
        "accountList":accountList,
        "accountTable": accountTable,
        "accountFilter": accountFilter,
        "ditLink":ditLink,
        "dttLink":dttLink,
        "hydraLink":hydraLink,
        "monitoringLink":monitoringLink,
        "ddpLink":ddpLink,
        "version":version,
        "doc2":doc2,
        "doc3":doc3,
        "doc4":doc4,
        "status":status,
        "message": system.status
    })

@user_passes_test(is_administrator_or_operator, login_url=reverse_lazy('manager:access_denied'))
def system_add(request):

    if request.method == "POST":
        form =  AddSystemForm(request.POST)
        form.attrs={'class': 'form', 'id': 'add_system'}
        if form.is_valid():
            name = form.cleaned_data['name']
            form.save()
            logger.info("System " + name + " added by "+ request.user.username)
            details_url = reverse('manager:system_details', kwargs={'system_name': name})
            return redirect( details_url)
   
    else:
        form = AddSystemForm()


    title1= "System"
    subtitle1 = "Add New"
    return render(request, "system-add.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
    })
@login_required
def system_remove(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(System, id=item_id)
                item_name = item.name
                item.delete()
                deleted_items.append({'id': item_id, 'name': item_name})
                logger.info("System: "+ item.name + "deleted by: " + request.user.username)

            except SystemType.DoesNotExist:
                # Handle the case where the item does not exist
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
                logger.error("Failed to delete system - Item not found id: "+ item_id + " by: " + request.user.username)
            except Exception as e:
                item.is_active = False
                item.password = None
                item.save()
                # Handle other exceptions (e.g., permission denied)
                logger.error("Failed to delete system: "+ item_id + " " + str(e) + " by: " + request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": str(e)})


    title1= "Remove"
    subtitle1 = "System Type(s)"
    return render(request, "remove-system.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "deleted_items":deleted_items,
        "failed_to_delete_items":failed_to_delete_items,
    })

@login_required
def system_manage(request,system_name):

    try:
        system = System.objects.get(name=system_name)
    except System.DoesNotExist:
        system = None

    if request.method == "POST":
        form =  ModSystemForm(request.POST,instance=system)
        form.attrs={'class': 'form', 'id': 'add_system'}
        if form.is_valid():
            name = form.cleaned_data['name']            
            form.save()
            logger.info("System " + system.name + " modified by "+ request.user.username)
            details_url = reverse('manager:system_details', kwargs={'system_name': name})
            return redirect( details_url)
    else:
        form = ModSystemForm(instance=system)

    title1= "System"
    subtitle1 = "Update"
    return render(request, "system-mod.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
    })

###################### ORDERS
@login_required
def order_decline(request):

       
    items = []  # Initialize an empty list to store deleted item IDs
    failed_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form
        comment = request.POST.get('comment')

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(Order, id=item_id)
                if "ENM" in str(item.system.type):

                    try:
                        enmuser =  ENMUser.objects.get(account = item.account, system = item.system )
                        enmuser.is_approved = True
                        enmuser.save()
                        enmuser.delete()
                    except ENMUser.DoesNotExist:
                        enmuser = None 
                           
                item.is_approved = False
                item.is_declined = True
                item.approved_by = request.user
                items.append({'id': item_id, 'account': item.account,'system': item.system})
                if comment != "":
                    item.comment = comment
                commentJira(item.jira_ticket.ticket_number,comment+"\nAccount: "+ item.account.name + " on system: " + item.system.name + "was rejected by: " + request.user.username)
                putJiraInProgress(item.jira_ticket.ticket_number)
                item.account.systems.remove(item.system)
                item.save()
                close_jira(item.jira_ticket.ticket_number)
                logger.info("Account: " + item.account.name + " on system "+ item.system.name + " rejected by " + request.user.username)

            except Order.DoesNotExist:
                # Handle the case where the item does not exist
                failed_items.append({'id': item_id, 'account': 'Item not found','system':"", "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                failed_items.append({'id': item_id, 'account': item.account,'system': item.system, "error": e})


    title1= "Reject"
    subtitle1 = "Account(s)"
    return render(request, "order-decline.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "items":items,
        "failed_items":failed_items,
    })

@login_required
def order_accept(request):

        
    items = []  # Initialize an empty list to store deleted item IDs
    failed_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form
        comment = request.POST.get('comment')
        if request.user.is_approver:
            approver = Approver.objects.get(user = request.user)
        else:
            approver = Approver(user = request.user )
            approver.save()
            request.user.is_approver = True
            request.user.save()

        for item_id in item_ids.split(","):

            try:
                item = get_object_or_404(Order, id=item_id)

                if "ENM" in str(item.system.type):

                    try:
                        enmuser =  ENMUser.objects.get(account = item.account, system = item.system )
                        enmuser.is_approved = True
                        enmuser.approved_by = approver
                    except ENMUser.DoesNotExist:
                        enmuser = ENMUser()
                        


                    if check_enmuser(enmuser.account.name, enmuser.system) != 0:
                        new_enm_account = create_enm_account(enmuser.account.name, enmuser.system, enmuser.profile )
                    else:
                        new_enm_account= 1

                    if new_enm_account == 1:
                        enmuser.save()
                        logger.info("ENM account: "+ enmuser.account.name + " on system" +enmuser.system.name +  " created" )
                        item.is_approved = True
                        item.is_declined = False
                    elif new_enm_account == 22:
                        logger.error("Can't establish session towards ENM: "+ enmuser.system.name )
                        raise Exception("Can't establish session towards ENM.")
                    elif new_enm_account == 27:
                        logger.error("Admin user and password not set for system: "+ enmuser.system.name )
                        raise Exception( "Admin user and password not set for system.")
                    else:
                        logger.error("ENM account "+enmuser.account.name+" not created.")
                        raise Exception( "ENM account not created.")
          

                item.approved_by = approver
                items.append({'id': item_id, 'account': item.account,'system': item.system})
                if comment != "":
                    item.comment = comment

                commentJira(item.jira_ticket.ticket_number,comment+"\nAccount: "+ item.account.name + " on system: " + item.system.name + " was accepted by: " + approver.user.username+"\n Please visit: " +'https://'+ request.get_host() + reverse('manager:my_profile')+ "\n and reset password for your system account")
                logger.info(item.jira_ticket.ticket_number + comment+"Account: "+ item.account.name + " on system: " + item.system.name + " was accepted by: " + approver.user.username)
                putJiraInProgress(item.jira_ticket.ticket_number)
                item.save()              
                close_jira(item.jira_ticket.ticket_number)
                account = Account.objects.get(pk=item.account.pk)
                account.is_active = True
                account.save()
                
            except Order.DoesNotExist:
                # Handle the case where the item does not exist
                failed_items.append({'id': item_id, 'account': 'Item not found','system':"", "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                failed_items.append({'id': item_id, 'account': item.account,'system': item.system, "error": e})


    title1= "Accepts"
    subtitle1 = "Account(s)"
    return render(request, "order-accept.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "items":items,
        "failed_items":failed_items,
    })

@login_required
def jira_list(request):

    try:
        if request.user.is_operator or request.user.is_adminstrator:
            orderList = JiraTicket.objects.all()
        else:
            jira_tickets_with_specific_account = JiraTicket.objects.filter(account__user=request.user)

            # Query JiraTicket objects associated with specific ordered_by value in Order
            jira_tickets_with_specific_ordered_by = JiraTicket.objects.filter(order__ordered_by_id=request.user)
            orderList = jira_tickets_with_specific_account | jira_tickets_with_specific_ordered_by
        
        orderFilter = JiraFilter(request.GET, queryset=orderList)
        orderTable = JiraTable(orderFilter.qs)
        RequestConfig(request).configure(orderTable)
    except JiraTicket.DoesNotExist:
        orderList = None  
        orderTable = None

    title1= "Jira"
    subtitle1 = "List "
  
    return render(request, "jira-list.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "orderList": orderList,
        "orderTable": orderTable,
        "orderFilter": orderFilter

    })

@login_required
def jira_details(request, jira_id):
    try:
        jira = JiraTicket.objects.get(ticket_number=jira_id)
    except JiraTicket.DoesNotExist:
        jira = None

    try:
        orderList = Order.objects.filter(jira_ticket = jira)
        orderFilter = OrderFilter(request.GET, queryset=orderList)
        orderTable = OrderTable(orderFilter.qs)
        RequestConfig(request).configure(orderTable)
    except Order.DoesNotExist:
        orderList = None  
        orderTable = None
  

    title1= "Jira"
    subtitle1 = "Details"

    return render(request, "jira-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "jira":jira,
        "orderTable": orderTable,
        "orderFilter": orderFilter
    })

@login_required
def order_list(request):

    try:
        if request.user.is_operator or request.user.is_adminstrator:
            orderList = Order.objects.all()
        else:
            orderList = Order.objects.filter( Q(account__user = request.user) | Q(ordered_by = request.user))
        orderFilter = OrderFilter(request.GET, queryset=orderList)
        orderTable = OrderTable(orderFilter.qs)
        RequestConfig(request).configure(orderTable)
    except Order.DoesNotExist:
        orderList = None  
        orderTable = None

    title1= "Order"
    subtitle1 = "List "
  
    return render(request, "order-list.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "orderList": orderList,
        "orderTable": orderTable,
        "orderFilter": orderFilter

    })

@login_required
def order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        order = None

    
    try:
        accounts = Account.objects.filter(pk = order.account.id, systems__pk = order.system.pk)
    except Account.DoesNotExist:
        accounts = None

    try:
        accountFilter = AccountFilter(request.GET, queryset=accounts)
        accountTable = AccountTable(accountFilter.qs)
        RequestConfig(request).configure(accountTable)
    except Account.DoesNotExist:
        accountTable = None    

    ### ENMUser accounts and profiles
    try:
        enmaccount = ENMUser.objects.filter(account__in= accounts)
    except ENMUser.DoesNotExist:
        enmaccount = None

    try:
        enmaccountFilter = ENMUserFilter(request.GET, queryset=enmaccount)
        enmaccountTable = ENMUserTable(enmaccountFilter.qs)
        RequestConfig(request).configure(enmaccountTable)
    except Approver.DoesNotExist:
        enmaccountFilter = None
        enmaccountTable = None 

    ### EOUser accounts and profiles
    try:
        eoaccount = EOUser.objects.filter(account__in= accounts)
    except EOUser.DoesNotExist:
        eoaccount = None

    try:
        eoaccountFilter = EOUserFilter(request.GET, queryset=eoaccount)
        eoaccountTable = EOUserTable(eoaccountFilter.qs)
        RequestConfig(request).configure(eoaccountTable)
    except Approver.DoesNotExist:
        eoaccountFilter = None
        eoaccountTable = None 

    ### EICUser accounts and profiles        
    try:
        eicaccount = EICUser.objects.filter(account__in= accounts)
    except EOUser.DoesNotExist:
        eoaccount = None

    try:
        eicaccountFilter = EICUserFilter(request.GET, queryset=eicaccount)
        eicaccountTable = EICUserTable(eicaccountFilter.qs)
        RequestConfig(request).configure(eicaccountTable)
    except Approver.DoesNotExist:
        eicaccountFilter = None
        eicaccountTable = None 
    ###


    title1= "Order"
    subtitle1 = "Details"

    return render(request, "order-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "order":order,
        "accounts":accounts,
        "accountTable": accountTable,
        "accountFilter": accountFilter,
        "enmaccountTable" : enmaccountTable,
        "enmaccountFilter" : enmaccountFilter,
        "eoaccountTable" : eoaccountTable,
        "eoaccountFilter" : eoaccountFilter,
        "eicaccountTable" : eicaccountTable,
        "eicaccountFilter" : eicaccountFilter
    })


# 
@login_required
def order_manage(request):

    if request.user.is_adminstrator or request.user.is_operator:
        approvalList = Order.objects.filter(is_approved=False, is_declined=False)
    elif request.user.is_approver:
        approver = Approver.objects.get(user_id=request.user.id)
        approvalList = Order.objects.filter(system__area__in=list(approver.area.values_list('pk', flat=True)), is_approved=False, is_declined=False)
    else:
        approvalList = None
        

    try:
        approvalFilter = OrderFilter(request.GET, queryset=approvalList)
        approvalTable = OrderTable(approvalFilter.qs)
        RequestConfig(request).configure(approvalTable)
    except Order.DoesNotExist:
        approvalList = None  
        approvalTable = None

    title1= "Pending"
    subtitle1 = "List"
  
    return render(request, "order-manage.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        #"approvalList": approvalList,
        "approvalTable": approvalTable,
        "approvalFilter": approvalFilter

    })

############# AREAS

@login_required
def area_list(request):

    try:
        areaList = Area.objects.all()
        areaFilter = AreaFilter(request.GET, queryset=areaList)
        areaTable = AreaTable(areaFilter.qs)
        RequestConfig(request).configure(areaTable)
    except Area.DoesNotExist:
        areaList = None  
        areaTable = None

    title1= "Areas"
    subtitle1 = "List"
  
    return render(request, "area-list.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "areaList": areaList,
        "areaTable": areaTable,
        "areaFilter": areaFilter
    })

@login_required
def area_details(request, area_name):

    try:
        area = Area.objects.get(name=area_name)
    except Area.DoesNotExist:
        area = None  

    try:
        systemList = System.objects.filter(area_id=area.id)
        systemFilter = SystemFilter(request.GET, queryset=systemList)
        systemTable = SystemTable(systemFilter.qs)
        RequestConfig(request).configure(systemTable)
    except Account.DoesNotExist:
        systemList = None  
        systemTable = None    

    title1= "Area"
    subtitle1 = "Details"

    users = AMSUser.objects.filter(area=area)
    
    return render(request, "area-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "area":area,
        "users": users,
        "systemList": systemList,
        "systemTable": systemTable,
        "systemFilter": systemFilter
    })


@login_required
def area_add(request):

    if request.method == "POST":
        form =  AddAreaForm(request.POST)
        form.attrs={'class': 'form', 'id': 'add_area'}
        if form.is_valid():
            name = form.cleaned_data['name']
            form.save()
            logger.info("Area " + name + " added by "+ request.user.username)
            details_url = reverse('manager:area_details', kwargs={'area_name': name})
            return redirect( details_url)
   
    else:
        form = AddAreaForm()


    title1= "Area"
    subtitle1 = "Add New"
    return render(request, "area-add.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
    })

@login_required
def area_manage(request, area_name):

    try:
        area = Area.objects.get(name=area_name)
    except Area.DoesNotExist:
        area = None  

    if request.method == "POST":

        form = AddAreaForm(request.POST,instance=area)
        form.attrs={'class': 'form', 'id': 'add_are'}
        if form.is_valid():
            name = form.cleaned_data['name']
            form.save()
            logger.info("Area " + name + " modified by "+ request.user.username)
            details_url = reverse('manager:area_details', kwargs={'area_name': name})
            return redirect( details_url)

    else:
        form = AddAreaForm(instance=area)

    title1= "Area"
    subtitle1 = "Update"

    return render(request, "area-mod.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
        "area": area
    })

def area_remove(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted

    
    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(Area, id=item_id)
                item_name = item.name
                item.delete()
                logger.info("Area " + item.name + " deleted by "+ request.user.username)
                deleted_items.append({'id': item_id, 'name': item_name})
            except Area.DoesNotExist:
                # Handle the case where the item does not exist
                logger.error("Failed to delete area - does not exists - by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                logger.error("Failed to delete area " + item.name + " error:" + e + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})

    
    title1= "Remove"
    subtitle1 = "Areas"
    return render(request, "remove-area.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "deleted_items":deleted_items,
        "failed_to_delete_items":failed_to_delete_items,
    })

######## APPROVERS

@login_required
def approver_list(request):

    try:
        approverList = Approver.objects.all()
        approverFilter = ApproverFilter(request.GET, queryset=approverList)
        approverTable = ApproverTable(approverFilter.qs)
        RequestConfig(request).configure(approverTable)
    except Order.DoesNotExist:
        approverList = None  
        approverTable = None

    title1= "Approver"
    subtitle1 = "List"
  
    return render(request, "approver-list.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "approverList": approverList,
        "approverTable": approverTable,
        "approverFilter": approverFilter

    })

@login_required
def approver_add(request):

    if request.method == "POST":
        form =  AddApproverForm(request.POST)
        form.attrs={'class': 'form', 'id': 'add_system_type'}
        if form.is_valid():
            user = form.cleaned_data['user']
            form.save()
            user.is_approver = True
            user.save()
            user.groups.add(Group.objects.get(name='Approvers') )
            logger.info("Approver " + user.username + " added by "+ request.user.username)
            details_url = reverse('manager:approver_details', kwargs={'approver_name': user.username})
            return redirect( details_url)
   
    else:
        form = AddApproverForm()


    title1= "Approver"
    subtitle1 = "Add New"
    return render(request, "approver-add.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
    })

@login_required
def approver_details(request, approver_name):
    try:
        approvers = Approver.objects.filter(user__username=approver_name)
    except Approver.DoesNotExist:
        approvers = None

    try:
        approverFilter = ApproverFilter(request.GET, queryset=approvers)
        approverTable = ApproverTable(approverFilter.qs)
        RequestConfig(request).configure(approverTable)
    except Approver.DoesNotExist:
        approverFilter = None
        approverTable = None    
        
    title1= "Approver"
    subtitle1 = "Details"

    return render(request, "approver-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "approvers":approvers,
        "approverTable": approverTable,
        "approverFilter": approverFilter
    })

@login_required
def approver_manage(request,approver_name):

    try:
        approver = Approver.objects.get(user__username=approver_name)
    except Approver.DoesNotExist:
        approver= Approver([])
        

    try:
        user = AMSUser.objects.get(username = approver_name)
    except AMSUser.DoesNotExist:    
        user = AMSUser([])

    if request.method == "POST":
        form =  ManageApproverForm(request.POST,instance=approver)
        form.attrs={'class': 'form', 'id': 'add_approver'}
        if form.is_valid():
            form.save()
            user.is_approver = True
            user.save()
            logger.info("Approver " + user.username + " modified by "+ request.user.username)
            user.groups.add(Group.objects.get(name='Approvers') )
            details_url = reverse('manager:approver_details', kwargs={'approver_name': user.username})
            return redirect( details_url)
   
    else:
        form = ManageApproverForm(instance=approver)


    title1= "Approver"
    subtitle1 = "Update"
    return render(request, "approver-mod.page.tmpl.html",{
        "title1": approver_name,
        "subtitle1": subtitle1,
        "form": form,
        "approver_name": approver_name,
    })

####### SYSTEM TYPE
@login_required
def system_type_list(request):

    try:
        systemTypeList = SystemType.objects.all()
        systemTypeFilter = SystemTypeFilter(request.GET, queryset=systemTypeList)
        systemTypeTable = SystemTypeTable(systemTypeFilter.qs)
        RequestConfig(request).configure(systemTypeTable)
    except Area.DoesNotExist:
        systemTypeList = None  
        systemTypeTable = None
      
    title1= "System Type"
    subtitle1 = "List"
  
    return render(request, "system-type-list.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "systemTypeList": systemTypeList,
        "systemTypeTable": systemTypeTable,
        "systemTypeFilter": systemTypeFilter,
    })

@login_required
def system_type_details(request, system_type_name):

    try:
        systemType = SystemType.objects.get(name=system_type_name)
    except SystemType.DoesNotExist:
        systemType = None  

    try:
        systemList = System.objects.filter(type_id=systemType.id)
        systemFilter = SystemFilter(request.GET, queryset=systemList)
        systemTable = SystemTable(systemFilter.qs)
        RequestConfig(request).configure(systemTable)
    except Account.DoesNotExist:
        systemList = None  
        systemTable = None    

    if "ENM" in str(system_type_name):
        profile_list = ENMUserProfile.objects.all()   
        profileFilter = ENMProfileFilter(request.GET, queryset=profile_list)
        profileTable = ENMProfileTable(profileFilter.qs)
                 
    elif "EIC" in str(system_type_name):
        profile_list = EICUserProfile.objects.all()
        profileFilter = EICProfileFilter(request.GET, queryset=profile_list)
        profileTable = EICProfileTable(profileFilter.qs)
    elif "EO" in str(system_type_name):
        profile_list = EOUserProfile.objects.all()
        profileFilter = EOProfileFilter(request.GET, queryset=profile_list)
        profileTable = EOProfileTable(profileFilter.qs)        
    else:
        profile_list = EICUserProfile([])
        profileTable = EOProfileTable([])
        profileFilter = EOProfileFilter([])

    RequestConfig(request).configure(profileTable)

    title1= "System Type"
    subtitle1 = "Details"

    return render(request, "system-type-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "systemType":systemType,
        "systemList": systemList,
        "systemTable": systemTable,
        "systemFilter": systemFilter,
        "profileTable" : profileTable,
        "profileFilter" : profileFilter
    })

@login_required
def system_type_add(request):

    if request.method == "POST":
        form =  AddSystemTypeForm(request.POST)
        form.attrs={'class': 'form', 'id': 'add_system_type'}
        if form.is_valid():
            name = form.cleaned_data['name']
            form.save()
            logger.info("System Type" + name + " added by "+ request.user.username)
            details_url = reverse('manager:system_type_details', kwargs={'system_type_name': name})
            return redirect( details_url)
    else:
        form = AddSystemTypeForm()

    title1= "System Type"
    subtitle1 = "Add New"
    return render(request, "system-type-add.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
    })

@login_required
def system_type_remove(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(SystemType, id=item_id)
                item_name = item.name
                item.delete()
                logger.info("System Type " + item.name + " deleted by "+ request.user.username)
                deleted_items.append({'id': item_id, 'name': item_name})
            except SystemType.DoesNotExist:
                # Handle the case where the item does not exist
                logger.error("Failed to delete System Type - does not exists - by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                logger.error("Failed to delete System Type " + item.name + " error:" + e + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})


    title1= "Remove"
    subtitle1 = "System Type(s)"
    return render(request, "remove-system-type.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "deleted_items":deleted_items,
        "failed_to_delete_items":failed_to_delete_items,
    })

@login_required
def system_type_manage(request,system_type_name):

    try:
        system_type = SystemType.objects.get(name=system_type_name)
    except:
        SystemType.DoesNotExist

    if request.method == "POST":
        form =  AddSystemTypeForm(request.POST,instance=system_type)
        form.attrs={'class': 'form', 'id': 'add_system_type'}
        if form.is_valid():
            name = form.cleaned_data['name']
            form.save()
            logger.info("System Type " + name + " modified by "+ request.user.username)
            details_url = reverse('manager:system_type_details', kwargs={'system_type_name': name})
            return redirect( details_url)
    else:
        form = AddSystemTypeForm(instance=system_type)

    title1= "System Type"
    subtitle1 = "Update"
    return render(request, "system-type-mod.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
    })

@login_required
def user_profile_details(request, system_type_group_name, profile_name):

    if "ENM" in str(system_type_group_name):
        role_list = list(ENMUserProfile.objects.get(name=profile_name).schema.values_list("name", flat=True)) 
    elif "EIC" in str(system_type_group_name):
        role_list = list(EICUserProfile.objects.get(name=profile_name).schema.values_list("name", flat=True)) 
    elif "EO" in str(system_type_group_name):
        role_list = list(EOUserProfile.objects.get(name=profile_name).schema.values_list("name", flat=True)) 

    title1= "User profile"
    subtitle1 = "Details"

    return render(request, "user-profile-details.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "role_list" : role_list,
        "profile_name" : profile_name,
        "system_type_group_name": system_type_group_name,
    })

@login_required
def user_profile_manage(request,system_type_group_name,profile_name):

    if system_type_group_name == "ENM":
        title1= "ENM Profile"
        try:
            profile = ENMUserProfile.objects.get(name=profile_name)
            if request.method == "POST":
                form =   AddENMProfileForm(request.POST,instance=profile)
            else:
                form =   AddENMProfileForm(instance=profile)
        except ENMUserProfile.DoesNotExist:
            profile = None
    elif system_type_group_name == "EO":    
        title1= "EO Profile"
        try:
            profile = EOUserProfile.objects.get(name=profile_name)
            if request.method == "POST":
                form =   AddEOProfileForm(request.POST,instance=profile)
            else:
                form =   AddEOProfileForm(instance=profile)
        except ENMUserProfile.DoesNotExist:
            profile = None   
    elif system_type_group_name == "EIC":  
        title1= "EIC Profile"  
        try:
            profile = EICUserProfile.objects.get(name=profile_name)
            if request.method == "POST":
                form =   AddEICProfileForm(request.POST,instance=profile)
            else:
                form =   AddEICProfileForm(instance=profile)
        except ENMUserProfile.DoesNotExist:
            profile = None

    if request.method == "POST":
        form.attrs={'class': 'form', 'id': 'manage_profile'}
        if form.is_valid():
            name = form.cleaned_data['name']        
            schema = form.cleaned_data['schema']    
            form.save()
            logger.info("User Profile " + name + " modified by "+ request.user.username)
            details_url = reverse('manager:user_profile_details', kwargs={'profile_name': name, 'system_type_group_name' : system_type_group_name})
            return redirect( details_url)


   
    subtitle1 = "Update"
    return render(request, "user-profile-mod.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
        "profile_name":profile_name,
        'system_type_group_name' : system_type_group_name
    })

@login_required
def user_profile_add(request, system_type_name):

    if request.method == "POST":
        if "ENM" in str(system_type_name):
            form =  AddENMProfileForm(request.POST)
                 
        elif "EIC" in str(system_type_name):
            form =  AddEICProfileForm(request.POST)

        elif "EO" in str(system_type_name):
              form =  AddEOProfileForm(request.POST)
        else:
            form = None

        form.attrs={'class': 'form', 'id': 'add_profile'}
        if form.is_valid():
            name = form.cleaned_data['name']
            form.save()
            logger.info("User Profile " + name + " added by "+ request.user.username)
            details_url = reverse('manager:system_type_details', kwargs={'system_type_name': system_type_name})
            return redirect(details_url)
   
    else:
        if "ENM" in str(system_type_name):
            form =  AddENMProfileForm()
                 
        elif "EIC" in str(system_type_name):
            form =  AddEICProfileForm()

        elif "EO" in str(system_type_name):
              form =  AddEOProfileForm()

    title1= "Profile"
    subtitle1 = "Add New"
    return render(request, "user-profile-add.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
        "system_type_name": system_type_name
    })

@login_required
def user_profile_remove_enm(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        system_type = request.POST.get('system_type')
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(ENMUserProfile, id=item_id)
                item_name = item.name
                item.delete()
                logger.info("ENM User Profile " + item.name + " deleted by "+ request.user.username)
                deleted_items.append({'id': item_id, 'name': item_name})
            except ENMUserProfile.DoesNotExist:
                # Handle the case where the item does not exist
                logger.error("Failed to delete ENM User Profile - does not exists - by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                logger.error("Failed to delete ENM User Profile " + item.name + " error:" + e + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})


    title1= "Remove"
    subtitle1 = "ENM User profile(s)"
    return render(request, "remove-user-profile.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "deleted_items":deleted_items,
        "failed_to_delete_items":failed_to_delete_items,
        "system_type":system_type,
    })

@login_required
def user_profile_remove_eic(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form
        system_type = request.POST.get('system_type')
        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(EICUserProfile, id=item_id)
                item_name = item.name
                item.delete()
                deleted_items.append({'id': item_id, 'name': item_name})
                logger.info("EIC User Profile " + item.name + " deleted by "+ request.user.username)
            except EICUserProfile.DoesNotExist:
                # Handle the case where the item does not exist
                logger.error("Failed to delete EIC User Profile - does not exists - by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                logger.error("Failed to delete EIC User Profile " + item.name + " error:" + e + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})


    title1= "Remove"
    subtitle1 = "EICUser profile(s)"
    return render(request, "remove-user-profile.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "deleted_items":deleted_items,
        "failed_to_delete_items":failed_to_delete_items,
        "system_type":system_type,
    })

@login_required
def user_profile_remove_eo(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form
        system_type = request.POST.get('system_type')
        
        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(EOUserProfile, id=item_id)
                item_name = item.name
                item.delete()
                deleted_items.append({'id': item_id, 'name': item_name})
                logger.info("EO User Profile " + item.name + " deleted by "+ request.user.username)
            except EOUserProfile.DoesNotExist:
                # Handle the case where the item does not exist
                logger.error("Failed to delete EO User Profile - does not exists - by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                logger.error("Failed to delete EO User Profile " + item.name + " error:" + e + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})

    title1= "Remove"
    subtitle1 = "EOUser profile(s)"
    return render(request, "remove-user-profile.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "deleted_items":deleted_items,
        "failed_to_delete_items":failed_to_delete_items,
        "system_type":system_type,
    })
    
    
@login_required
def user_role_add(request, system_type_name):

    if request.method == "POST":
        if "ENM" in str(system_type_name):
            form =  AddENMRoleForm(request.POST)
                 
        elif "EIC" in str(system_type_name):
            form =  AddEICRoleForm(request.POST)

        elif "EO" in str(system_type_name):
              form =  AddEORoleForm(request.POST)
        else:
            form = None

        form.attrs={'class': 'form', 'id': 'add_profile'}
        if form.is_valid():
            name = form.cleaned_data['name']
            form.save()
            logger.info(system_type_name + " ROLE " + name + " Added by "+ request.user.username)
            details_url = reverse('manager:system_type_details', kwargs={'system_type_name': system_type_name})
            return redirect(details_url)
   
    else:
        if "ENM" in str(system_type_name):
            form =  AddENMRoleForm()
                 
        elif "EIC" in str(system_type_name):
            form =  AddEICRoleForm()

        elif "EO" in str(system_type_name):
              form =  AddEORoleForm()

    title1= "Role"
    subtitle1 = "Add New"
    return render(request, "user-role-add.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "form": form,
        "system_type_name": system_type_name
    })


@login_required
def reset_enmpassword(request,account_id,system_name):
    
    account = Account.objects.get(id=account_id)
    system = System.objects.get(name = system_name)


    if account.user != request.user:
        title1 = "Reset"
        subtitle1 = "ENM password"
        status = "ERROR"
        message = "You are not the owner of "+account.name+" on "+system_name

        return render(request, "reset-enmpassword-post.page.tmpl.html",{
                "title1": title1,
                "subtitle1": subtitle1,
                "message": message,
                "status": status
            })
    
    if request.method == "POST":
            
            logger.info("Reset password for: "+ account.name+" on system:" + system_name)
            try:
                if not ENMUser.objects.filter( system = system, account = account, is_approved = True ).exists():
                    status = "ERROR"
                    raise Exception("ENMUser is not approved yet")

                password = reset_password_on_enm(account.name,system_name)
            
                if password == 27:
                    status = "ERROR"
                    message = "Can't reset password."
                    logger.error("Password reset problem: "+ account.name + " on system: " + system_name )
                    raise Exception (status + " " + message)
                elif password == 28:
                    status = "ERROR"
                    message = "Can't get SED."
                    logger.error("Password reset problem: "+ account.name + " on system: " + system_name )
                    raise Exception (status + " " + message)
                elif password == 22:
                    status = "ERROR"
                    message = "Can't establish session towards ENM."
                    logger.error("Password reset problem: "+ account.name + " on system: " + system_name )
                    raise Exception (status + " " + message)
                else:
                    status = "OK"
                    message = "New password for "+account.name+" on system "+system_name+" has been reset to: "+password
                    logger.info("New password for "+account.name+" on system "+system_name+" has been reset")
            except Exception as e:
                status = "ERROR"
                message = ("Password reset issue: " + str(e))
                logger.error("Password reset issue: " + str(e))
            
            title1 = "Reset"
            subtitle1 = "ENM password"
            return render(request, "reset-enmpassword-post.page.tmpl.html",{
                "title1": title1,
                "subtitle1": subtitle1,
                #"account_id": account_id,
                #"account_name": account.name,
                #"system_name": system_name,
                "message": message,
                "status": status
            })
    else:
        title1= "Reset"
        subtitle1 = "ENM password"
        
        return render(request, "reset-enmpassword.page.tmpl.html",{
            "title1": title1,
            "subtitle1": subtitle1,
            "account_id": account_id,
            "account_name": account.name,
            "system_name": system_name
        })

@login_required
def account_remove_eic(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(EICUser, id=item_id)
                item_name = item.account.name + ' on ' + item.system.name
                remove_system_account_helper(item.account, item.system)
                check_if_account_active(item.account)
                logger.info("EIC system account: " + item_name + " deleted by" + request.user.username )
                deleted_items.append({'id': item_id, 'name': item_name})
            except Account.DoesNotExist:
                # Handle the case where the item does not exist
                check_if_account_active(item.account)
                logger.error("Failed to delete EIC system account with id: " + item_id + " object does not exists")
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                check_if_account_active(item.account)
                logger.error("Failed to delete EIC system account " + item_name + " error:" + str(e) + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})
@login_required
def account_remove_eo(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(EOUser, id=item_id)
                item_name = item.account.name + ' on ' + item.system.name
                remove_system_account_helper(item.account, item.system)
                check_if_account_active(item.account)
                logger.info("EO system account: " + item_name + " deleted by" + request.user.username )
                deleted_items.append({'id': item_id, 'name': item_name})
            except Account.DoesNotExist:
                # Handle the case where the item does not exist
                check_if_account_active(item.account)
                logger.error("Failed to delete EO system account with id: " + item_id + " object does not exists")
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                check_if_account_active(item.account)
                logger.error("Failed to delete EO system account " + item_name + " error:" + str(e) + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})\
                
@login_required
def account_remove_enm(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(ENMUser, id=item_id)
                item_name = item.account.name + ' on ' + item.system.name
                remove_system_account_helper(item.account, item.system)
                check_if_account_active(item.account)
                logger.info("ENM system account: " + item_name + " deleted by" + request.user.username )
                deleted_items.append({'id': item_id, 'name': item_name})
            except Account.DoesNotExist:
                # Handle the case where the item does not exist
                check_if_account_active(item.account)
                logger.error("Failed to delete ENM system account with id: " + item_id + " object does not exists")
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                check_if_account_active(item.account)
                logger.error("Failed to delete EMM system account " + item_name + " error:" + str(e) + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})


    title1= "Remove"
    subtitle1 = "ENM Account"
    return render(request, "remove-account.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "deleted_items":deleted_items,
        "failed_to_delete_items":failed_to_delete_items,
    })

@login_required
def account_remove(request):
    
    deleted_items = []  # Initialize an empty list to store deleted item IDs
    failed_to_delete_items = []  # Initialize an empty list to store IDs of items that couldn't be deleted


    if request.method == 'POST':
        item_ids = request.POST.get('selected_rows')  # Assuming you have checkboxes with item IDs in your form

        for item_id in item_ids.split(","):
            try:
                item = get_object_or_404(Account, id=item_id)
                item_name = item.name
                remove_account_helper(item)
                check_if_account_active(item)
                logger.info("AMS account: " + item_name + " deleted by" + request.user.username )
                deleted_items.append({'id': item_id, 'name': item_name})
            except Account.DoesNotExist:
                # Handle the case where the item does not exist
                check_if_account_active(item)
                logger.error("Failed to delete AMS account with id: " + item_id + " object does not exists")
                failed_to_delete_items.append({'id': item_id, 'name': 'Item not found', "error":""})
            except Exception as e:
                # Handle other exceptions (e.g., permission denied)
                check_if_account_active(item)
                logger.error("Failed to delete AMS account " + item_name + " error:" + str(e) + " by " +request.user.username)
                failed_to_delete_items.append({'id': item_id, 'name': item_name, "error": e})


    title1= "Remove"
    subtitle1 = "System Type(s)"
    return render(request, "remove-account.page.tmpl.html",{
        "title1": title1,
        "subtitle1": subtitle1,
        "deleted_items":deleted_items,
        "failed_to_delete_items":failed_to_delete_items,
    })

