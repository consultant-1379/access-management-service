import django_tables2 as tables
from .models import *
from django.utils.html import format_html
from django.urls import reverse
from django_tables2.utils import Accessor


class SystemTable(tables.Table):

    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
        
  
    def render_actions(self,record):
        manage_url = reverse('manager:system_manage', kwargs={'system_name': record.name})
        orders_url = reverse('manager:account_order')
        if self.request.user.is_operator:     
            return format_html('<a href="{}" class="btn"><i class="icon icon-settings"></i>{}</a>&nbsp', manage_url, 'edit') + format_html('<a href="{}" class="btn"><i class="icon icon-tasks"></i>{}</a>&nbsp', orders_url, 'order account') + format_html('<button id="open-warning"  class="btn warning dialog-button system" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, record.name, 'remove')
        else:
            return format_html('<a href="{}" class="btn"><i class="icon icon-tasks"></i>{}</a>', orders_url, 'order account')
    
    def render_name (self, value, record):
        details_url = reverse('manager:system_details', kwargs={'system_name': record.name})
        return format_html('<a href="{}">{}</a>', details_url, value)

        
    class Meta:
        model = System
        fields = ('name', 'area', 'type','is_active')
        attrs = {"class": "table", "id" : "systems"}
        sequence = ('name', 'type', 'area','is_active','actions','selection')
        paginate = False 



class AccountTable(tables.Table):
    
    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
    #created = tables.Column( empty_values=(),orderable=False)
  
    def render_actions(self,record):
        #manage_url = reverse('manager:account_list', kwargs={'account_name': record.name})
        
        if self.request.user.is_operator and record.is_active:     
            return format_html('<button id="open-warning"  class="btn warning dialog-button account" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, record.name, 'remove')
        else:
            return "-"
    
    def render_name (self, value, record):
        details_url = reverse('manager:account_details', kwargs={'account_name': record.name})
        return format_html('<a href="{}">{}</a>', details_url, value)
    
    class Meta:
        model = Account
        fields = ('name', 'user', 'systems','is_active','created_at','updated_at')
        attrs = {"class": "table", "id" : "accounts"}
        sequence = ('name', 'user', 'systems','is_active','created_at','updated_at','actions','selection')
 #       paginate = False 

class OrderTable(tables.Table):

    actions = tables.Column( empty_values=(),orderable=False)
    id = tables.Column(verbose_name="#")
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
    profile = tables.Column( empty_values=(),orderable=False,verbose_name="Profile")
    area = tables.Column( empty_values=(),orderable=False,verbose_name="Area")

    def render_area(self,record):
      return str(record.system.area.name)

    def render_id (self, value, record):
        details_url = reverse('manager:order_details', kwargs={'order_id': record.id})
        return format_html('<a href="{}">{}</a>', details_url, value)

    def render_profile(self,record):
        
        if "ENM" in str(record.system.type):

            try:
                enmuser = ENMUser.objects.get(account = record.account,system=record.system)

            except ENMUser.DoesNotExist:
                return "-"

            details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"ENM",'profile_name': enmuser.profile.name})
            
            return format_html('<span title="{}"><a href="{}">{}</a></span>',list(enmuser.profile.schema.values_list("name", flat=True)), details_url, enmuser.profile)
        
        elif "EIC" in str(record.system.type):
            return "EIC profile"

        elif "EO" in str(record.system.type):
            try:
                eouser = EOUser.objects.get(account = record.account,system=record.system)

            except EOUser.DoesNotExist:
                eouser = []

            details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"EO",'profile_name': eouser.profile.name})
            
            return format_html('<span title="{}"><a href="{}">{}</a></span>',list(eouser.profile.schema.values_list("name", flat=True)), details_url, eouser.profile)

        elif "PTEaaS" in str(record.system.type):
            return "PTEaaS profile"
            
        else:
            return "-"
        
    
    def render_jira_ticket (self, value, record):
        details_url = reverse('manager:jira_details', kwargs={'jira_id': record.jira_ticket})
        return format_html('<a href="{}">{}</a>', details_url, value)

    def render_actions(self,record):
        try:
            approver = Approver.objects.get(user_id=self.request.user)
            area_list = list(approver.area.values_list('pk', flat=True))
        except Approver.DoesNotExist:
            approver = Approver([])
            area_list = []
        if (self.request.user.is_operator or self.request.user.is_adminstrator or (self.request.user.is_approver and record.system.area.id in area_list ))and record.is_approved == False and record.is_declined == False:     
            return format_html('<button id="open-warning"  class="btn primary accept-button" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, f"{record.account} on {record.system}" , 'approve') + \
                format_html('<button id="open-warning"  class="btn warning decline-button" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, f"{record.account} on {record.system}" , 'decline')
        return "-"
   
       
    class Meta:
        model = Order
        fields = ('id','account', 'area','profile', 'jira_ticket', 'is_approved', 'is_declined', 'ordered_by','system','comment','created_at','updated_at','actions', 'selection')
        attrs = {"class": "table", "id" : "order"}
        sequence = ('id','account','area', 'profile', 'jira_ticket','is_approved','is_declined', 'ordered_by','system','comment','created_at','updated_at')

class AreaTable(tables.Table):

    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
        
  
    def render_actions(self,record):
        #manage_url = reverse('manager:account_list', kwargs={'account_name': record.name})
        manage_url = reverse('manager:area_manage', kwargs={'area_name': record.name})
    
        if self.request.user.is_operator:     
            return format_html('<a href="{}" class="btn"><i class="icon icon-settings"></i>{}</a>&nbsp', manage_url, 'manage') + format_html('<button id="open-warning"  class="btn warning dialog-button" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, record.name, 'remove')
    
    def render_name (self, value, record):
        details_url = reverse('manager:area_details', kwargs={'area_name': record.name})
        return format_html('<a href="{}">{}</a>', details_url, value)

        
    class Meta:
        model = Area
        fields = ('name', 'users')
        attrs = {"class": "table", "id" : "order"}
        sequence = ('name', 'users','actions','selection')
        paginate = False 


class SystemTypeTable(tables.Table):

    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
        
  
    def render_actions(self,record):
        #manage_url = reverse('manager:account_list', kwargs={'account_name': record.name})
        manage_url = reverse('manager:system_type_manage',kwargs={'system_type_name': record.name})

        if self.request.user.is_operator:     
            return format_html('<a href="{}" class="btn"><i class="icon icon-settings"></i>{}</a>&nbsp', manage_url, 'manage') + format_html('<button id="open-warning"  class="btn warning dialog-button system-type" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, record.name, 'remove')

  
    def render_name (self, value, record):
        details_url = reverse('manager:system_type_details', kwargs={'system_type_name': record.name})
        return format_html('<a href="{}">{}</a>', details_url, value)

        
    class Meta:
        model = SystemType
        fields = ('name',)
        attrs = {"class": "table", "id" : "order"}
        sequence = ('name','actions','selection')
        #paginate = False 

class ApproverTable(tables.Table):

    actions = tables.Column( empty_values=(),orderable=False)
    
    def render_actions(self,record):
        #manage_url = reverse('manager:account_list', kwargs={'account_name': record.name})
        manage_url = reverse('manager:approver_manage', kwargs={'approver_name': record.user.username})
        if self.request.user.is_operator:     
            return format_html('<a href="{}" class="btn"><i class="icon icon-settings"></i>{}</a>&nbsp', manage_url, 'manage')
    
    def render_user (self, value, record):
        details_url = reverse('manager:approver_details', kwargs={'approver_name': record.user.username})
        return format_html('<a href="{}">{}</a>', details_url, value)

    class Meta:
        model = Approver
        fields = ('user' ,'area')
        attrs = {"class": "table", "id" : "order"}
        sequence = ('user','area','actions')
        paginate = False 


class ENMUserTable(tables.Table):

    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)

    def render_actions(self,record):
        #manage_url = reverse('manager:account_details', kwargs={'account_name': record.system})
        reset_url = reverse('manager:reset_enmpassword', kwargs={'account_id': record.account_id,'system_name': record.system})
    
        if self.request.user.is_operator or self.request.user == record.account.user :     
            return format_html('<button id="open-warning"  class="btn warning dialog-button enm" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, record.account.name +" on "+record.system.name, 'remove') + format_html('<a href="{}" class="btn"><i class="icon icon-no-task"></i>{}</a>&nbsp', reset_url, 'reset password')
        else:
            return format_html('-')
        
    def render_profile (self, value, record):
        details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"ENM",'profile_name': record.profile.name})
        return format_html('<span title="{}"><a href="{}">{}</a></span>',list(record.profile.schema.values_list("name", flat=True)), details_url, value)

    class Meta:
        model = ENMUser
        fields = ('account', 'system', 'profile','is_approved')
        attrs = {"class": "table", "id" : "order"}
        sequence = ('account', 'system', 'profile', 'is_approved','actions','selection')
        paginate = False 

class EOUserTable(tables.Table):

    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
        
    def render_actions(self,record):
        reset_url = reverse('manager:orders_list')

        if self.request.user.is_operator:     
            return format_html('<button id="open-warning"  class="btn warning dialog-button eo" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, record.account.name +" on "+record.system.name, 'remove') + format_html('<a href="{}" class="btn"><i class="icon icon-no-task"></i>{}</a>&nbsp', reset_url, 'reset password')
        else:
            return format_html('<a href="{}" class="btn"><i class="icon icon-no-task"></i>{}</a>&nbsp', reset_url, 'reset password')
    
    def render_profile (self, value, record):
        details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"EO",'profile_name': record.profile.name})
        return format_html('<span title="{}"><a href="{}">{}</a></span>',list(record.profile.schema.values_list("name", flat=True)), details_url, value)

    
    class Meta:
        model = EOUser
        fields = ('account', 'system', 'profile','is_approved')
        attrs = {"class": "table", "id" : "order"}
        sequence = ('account', 'system', 'profile', 'is_approved','actions','selection')
        paginate = False 

class EICUserTable(tables.Table):

    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
        
    def render_actions(self,record):
        manage_url = reverse('manager:orders_list')
        if self.request.user.is_operator:     
            return format_html('<a href="{}"><i class="icon icon-settings"></i>{}</a>&nbsp', manage_url, 'manage') + format_html('<button id="open-warning"  class="btn warning dialog-button eic" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>&nbsp', record.id, record.account.name +" on "+record.system.name, 'remove')
        else:
            return format_html('<a href="{}"><i class="icon icon-no-task"></i>{}</a>', manage_url, 'remove')
        
    def render_profile (self, value, record):
        details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"EIC",'profile_name': record.profile.name})
        return format_html('<span title="{}"><a href="{}">{}</a></span>',list(record.profile.schema.values_list("name", flat=True)), details_url, value)

    
    class Meta:
        model = EICUser
        fields = ('account', 'system', 'profile','is_approved')
        attrs = {"class": "table", "id" : "order"}
        sequence = ('account', 'system', 'profile', 'is_approved','actions','selection')
        paginate = False 

class ENMProfileTable(tables.Table):
    schema = tables.ManyToManyColumn(verbose_name="Roles")
    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
        
    def render_name (self, value, record):
        details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"ENM",'profile_name': record.name})
        return format_html('<a href="{}">{}</a>', details_url, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns['schema'].column.attrs = {"td":{"style" : "width:50%;" }}


    def render_actions(self,record):
        manage_url = reverse('manager:user_profile_manage', kwargs={'system_type_group_name':"ENM",'profile_name':record.name })
        if self.request.user.is_operator:     
            return format_html('<a class="btn" href="{}"><i class="icon icon-settings"></i>{}</a>', manage_url, 'edit') + format_html('<button id="open-warning"  class="btn warning dialog-button enm" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>', record.id, record.name, 'remove')
    
    class Meta:
        model = ENMUserProfile
        fields = ('name', 'schema', 'actions', 'selection')
        attrs = {"class": "table", "id" : "profile", "style":"max-width : 30 %"}
        sequence = ('name', 'schema','actions', 'selection')
        paginate = False

class ENMProfileTableShort(tables.Table):
    schema = tables.ManyToManyColumn(verbose_name="Roles")
        
    def render_name (self, value, record):
        details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"ENM",'profile_name': record.name})
        return format_html('<a href="{}">{}</a>', details_url, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns['schema'].column.attrs = {"td":{"style" : "width:50%;" }}
    
    class Meta:
        model = ENMUserProfile
        fields = ('name', 'schema')
        attrs = {"class": "table", "id" : "profile", "style":"max-width : 30 %"}
        sequence = ('name', 'schema')
        paginate = False

class EICProfileTable(tables.Table):
    schema = tables.ManyToManyColumn(verbose_name="Roles")
    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
        
    def render_name (self, value, record):
        details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"ENM",'profile_name': record.name})
        return format_html('<a href="{}">{}</a>', details_url, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns['schema'].column.attrs = {"td":{"style" : "width:50%;" }}


    def render_actions(self,record):
        manage_url = reverse('manager:user_profile_manage', kwargs={'system_type_group_name':"EIC",'profile_name':record.name })
        if self.request.user.is_operator:     
            return format_html('<a class="btn" href="{}"><i class="icon icon-settings"></i>{}</a>', manage_url, 'edit') + format_html('<button id="open-warning"  class="btn warning dialog-button eic" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>', record.id, record.name, 'remove')
    

    class Meta:
        model = EICUserProfile
        fields = ('name', 'schema')
        attrs = {"class": "table", "id" : "profile"}
        sequence = ('name', 'schema')
        paginate = False     
          
class EOProfileTable(tables.Table):
    schema = tables.ManyToManyColumn(verbose_name="Roles")
    actions = tables.Column( empty_values=(),orderable=False)
    selection = tables.TemplateColumn('<input type="checkbox" value="{{ record.pk }}" id="cb{{ record.pk }}" /><label for="cb{{ record.pk }}"></label>',orderable=False)
        
    def render_name (self, value, record):
        details_url = reverse('manager:user_profile_details', kwargs={'system_type_group_name':"EO",'profile_name': record.name})
        return format_html('<a href="{}">{}</a>', details_url, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns['schema'].column.attrs = {"td":{"style" : "width:50%;" }}


    def render_actions(self,record):
        manage_url = reverse('manager:user_profile_manage', kwargs={'system_type_group_name':"ENM",'profile_name':record.name })
        if self.request.user.is_operator:     
            return format_html('<a class="btn" href="{}"><i class="icon icon-settings"></i>{}</a>', manage_url, 'edit') + format_html('<button id="open-warning"  class="btn warning dialog-button eo" value="{}" name="{}" ><i class="icon icon-no-task"></i>{}</button>', record.id, record.name, 'remove')
    

    class Meta:
        model = EOUserProfile
        fields = ('name', 'schema')
        attrs = {"class": "table", "id" : "profile"}
        sequence = ('name', 'schema')
        paginate = False         


class JiraTable(tables.Table):


    status = tables.Column( empty_values=(),orderable=False,verbose_name="Orders ack/rej/total")

   
    def render_ticket_number (self, value, record):
        details_url = reverse('manager:jira_details', kwargs={'jira_id': record.ticket_number})
        return format_html('<a href="{}">{}</a>', details_url, value)

    def render_status(self,record):
        try:
            orders = Order.objects.filter(jira_ticket__ticket_number = record.ticket_number)

        except Order.DoesNotExist:
            orders = []

       
        ack_count = 0
        rej_count = 0
        for order in orders:
            if order.is_declined == True:
                rej_count = rej_count +1
            if order.is_approved == True:
                ack_count = ack_count +1

        status = str(ack_count) + "/" + str(rej_count) +"/" + str(len(orders))  
        return format_html('<label id="order status" value="">{}</label>', status) 

   
       
    class Meta:
        model = JiraTicket
        fields = ('account', 'ticket_number', 'is_closed', 'description','created_at','updated_at', 'status')
        attrs = {"class": "table", "id" : "jira"}
        sequence = ( 'ticket_number','account', 'is_closed', 'description','created_at','updated_at', 'status')

