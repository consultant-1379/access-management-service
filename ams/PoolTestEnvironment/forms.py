from django import forms
from .models import *

class PartialBookingForm(forms.ModelForm):
    team = forms.ModelChoiceField(queryset=Team.objects.all())
    booking_start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    booking_end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    # tls_enabled = forms.BooleanField(help_text='Check this box if want TLS Enabled.')
    tls_enabled = forms.ChoiceField(
        choices=[(True, 'True'), (False, 'False')],
        widget=forms.Select,
        initial=False,
    )
    jira_id = forms.CharField(required=False)
    app_set = forms.CharField()
    jira_comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}))

    class Meta:
        model = Booking
        fields = ['team', 'app_set', 'eic_version','booking_start_date','booking_end_date','jira_id','tls_enabled']  
        help_texts = {
            'app_set': 'Enter the EIC apps you need installed seperated by a space. E.g. dmm adc',
            'eic_version': 'Leave as 0.0.0 for latest version, or specify an exact version',
            'booking_start_date' : 'The default is set to today',
            'tls_enabled' : 'Check to enable TLS',
            'booking_end_date' : 'The normal booking length is two weeks. For bookings in excess of 2 week PM approval is required.',
            'jira_id' : 'Leave blank to auto create ticket based on entered data. Enter jira ID if one is already created.',
        }

        def save(self, commit=True):
            instance = super().save(commit=False)
            # Use self.cleaned_data['add field'] - do someting with added fields outside of normal model fields
            if commit:
                instance.save()
            return instance

        # def clean_tags(self):
        #     # """Process the 'tags' field and return a string of space-separated tag names."""
        #     tags = self.cleaned_data.get('app_set')
        #     return ' '.join(tag.name for tag in tags)


class BookingForm(forms.ModelForm):
    tls_enabled = forms.ChoiceField(
        choices=[(True, 'True'), (False, 'False')],
        widget=forms.Select,
        initial=False,
    )
    class Meta:
        model = Booking
        fields = '__all__'