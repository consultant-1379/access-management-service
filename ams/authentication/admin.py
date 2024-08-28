from django.contrib import admin
from .models import AMSUser
from .forms import AMSUserCreationForm
from django.contrib.auth.admin import UserAdmin


# Register your models here.
class AMSUserAdmin(UserAdmin):
    model = AMSUser
    add_form = AMSUserCreationForm

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'User role',
            {
                'fields': (
                    'is_adminstrator',
                    'is_operator',
                    'is_approver',
                    'is_pool_user',
                    'is_pool_admin',
                )
            }
        )
    )

admin.site.register(AMSUser, AMSUserAdmin)

