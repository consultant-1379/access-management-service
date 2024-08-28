import django_filters
from .models import *
from django import forms
from django.db.models import Q


class NamespaceFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')

    class Meta:
        model = Namespace
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(booking__team__name__icontains=value) |
            Q(booking__jira_id__icontains=value)
        )