from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'manager'

urlpatterns = [
    path('my-profile', views.my_profile, name='my_profile'),
    path('account/list', views.account_list, name='accounts_list'),
    path('account/remove', views.account_remove, name='account_remove'),
    path('account/remove_enm', views.account_remove_enm, name='account_remove_enm'),
    path('account/remove_eo', views.account_remove_eo, name='account_remove_eo'),
    path('account/remove_eic', views.account_remove_eic, name='account_remove_eic'),
    path('account/<account_name>/details', views.account_details, name='account_details'),
    path('account/order', views.AddOrderView.as_view(), name='account_order'),
    path('account/add', views.AddAccountView.as_view(), name='account_add'),
    path('area/add', views.area_add, name='area_add'),
    path('area/<area_name>/manage', views.area_manage, name='area_manage'),
    path('area/list', views.area_list, name='area_list'),
    path('area/<area_name>/details', views.area_details, name='area_details'),
    path('area/remove', views.area_remove, name='area_remove'),
    path('system/remove', views.system_remove, name='system_remove'),
    path('system/list', views.system_list, name='systems_list'),
    path('system/add', views.system_add, name='system_add'),
    path('system/<system_name>/manage', views.system_manage, name='system_manage'),
    path('system/<system_name>/send_email', views.system_email_send, name='system_email_send'),
    path('system/<system_name>/set_status', views.system_status_set, name='system_status_set'),
    path('system/<system_name>/clear_status', views.system_status_clear, name='system_status_clear'),
    path('system/<system_name>/details', views.system_details, name='system_details'),
    path('order/list', views.jira_list, name='orders_list'),
    path('order/<order_id>/details', views.order_details, name='order_details'),
    path('jira/<jira_id>/details', views.jira_details, name='jira_details'),
    path('order/manage', views.order_manage, name='order_manage'),
    path('order/accept', views.order_accept, name='order_accept'),
    path('order/decline', views.order_decline, name='order_decline'),
    path('system-type/list', views.system_type_list, name='system_type_list'),
    path('system-type/add', views.system_type_add, name='system_type_add'),
    path('system-type/user_profile_remove_enm', views.user_profile_remove_enm, name='user_profile_remove_enm'),
    path('system-type/user_profile_remove_eo', views.user_profile_remove_eo, name='user_profile_remove_eo'),
    path('system-type/user_profile_remove_eic', views.user_profile_remove_eic, name='user_profile_remove_eic'),
    path('system-type/<system_type_name>/details', views.system_type_details, name='system_type_details'),
    path('system-type/<system_type_name>/add_profile', views.user_profile_add, name='user_profile_add'),
    path('system-type/<system_type_name>/add_role', views.user_role_add, name='user_role_add'),
    path('system-type/<system_type_name>/manage', views.system_type_manage, name='system_type_manage'),
    path('system-type/<system_type_group_name>/<profile_name>/manage', views.user_profile_manage, name='user_profile_manage'),
    path('system-type/<system_type_group_name>/<profile_name>/details', views.user_profile_details, name='user_profile_details'),
    path('system-type/remove', views.system_type_remove, name='system_type_remove'),
    path('approver/list', views.approver_list, name='approver_list'),
    path('approver/<approver_name>/manage', views.approver_manage, name='approver_manage'),
    path('approver/add', views.approver_add, name='approver_add'),
    path('approver/<approver_name>/details', views.approver_details, name='approver_details'),
    path('reset/<account_id>/<system_name>',views.reset_enmpassword,name='reset_enmpassword'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('jira-failed/', views.jira_failed, name='jira_failed'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)