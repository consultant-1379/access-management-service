import django_filters
from .models import *
from django import forms


class SystemFilter(django_filters.FilterSet):
    area =  django_filters.ModelChoiceFilter(
        queryset = Area.objects.all(),
        widget = forms.Select(attrs={'class': 'btn'})
                
    )

    type =  django_filters.ModelChoiceFilter(
        queryset = SystemType.objects.all(),
        widget = forms.Select(attrs={'class': 'btn'})
                
    )    
    

    class Meta:
        model = System
        fields = ['name', 'area', 'type']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }

class AccountFilter(django_filters.FilterSet):

    class Meta:
        model = Account
        fields = ['name', 'user', 'systems',]
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }

class OrderFilter(django_filters.FilterSet):

    class Meta:
        model = Order
        fields = ['account', 'jira_ticket' , 'is_approved']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }  

class JiraFilter(django_filters.FilterSet):

    class Meta:
        model = JiraTicket
        fields = ['account', 'ticket_number' , 'is_closed']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }  

class AreaFilter(django_filters.FilterSet):

    class Meta:
        model = Area
        fields = ['name', 'users']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }

class SystemTypeFilter(django_filters.FilterSet):

    class Meta:
        model = SystemType
        fields = ['name']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }

class ApproverFilter(django_filters.FilterSet):

    class Meta:
        model = Approver
        fields = ['user', 'area']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }

class ENMUserFilter(django_filters.FilterSet):

    class Meta:
        model = ENMUser
        fields = ['account', 'system', 'profile','is_approved']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }

class ENMProfileFilter(django_filters.FilterSet):

    class Meta:
        model = ENMUserProfile
        fields = ['name', 'schema']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }

class EICProfileFilter(django_filters.FilterSet):

    class Meta:
        model = EICUserProfile
        fields = ['name', 'schema']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }                

class EOProfileFilter(django_filters.FilterSet):

    class Meta:
        model = ENMUserProfile
        fields = ['name', 'schema']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }        


class EOUserFilter(django_filters.FilterSet):

    class Meta:
        model = EOUser
        fields = ['account', 'system', 'profile','is_approved']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }


class EICUserFilter(django_filters.FilterSet):

    class Meta:
        model = EICUser
        fields = ['account', 'system', 'profile','is_approved']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }

class EOProfileFilter(django_filters.FilterSet):

    class Meta:
        model = EOUserProfile
        fields = ['name', 'schema']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                    'widget': forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'Type here ...'})
                },
            },

        }
