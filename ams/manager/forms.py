from django import forms
from .models import *
from authentication.models import AMSUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class AddSystemForm(forms.ModelForm):
    type = forms.ModelChoiceField(queryset=SystemType.objects.all(),widget=forms.Select(attrs={'class': 'select'}))
    area = forms.ModelChoiceField(queryset=Area.objects.all(), widget=forms.Select(attrs={'class': 'select'}))
    name = forms.CharField(label='System Name', max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New system name'}))
    admin = forms.CharField(label='Admin Account',max_length=50,widget=forms.TextInput(attrs={'class': 'validation', 'type': 'username', 'placeholder': 'System Admin username'}))
    password = forms.CharField(label='Admin User password',max_length=50,widget=forms.PasswordInput(attrs={'class': 'validation', 'type': 'password', 'placeholder': 'System Admin password','style':'max-width:220px'}))
    

    #attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'System Admin password'}
    class Meta:
        model = System
        fields = ['type', 'area', 'name','admin','password']
        labels = {"type": "System Type", "area": "Area", "name": "Name","admin":"Admin","password":"Password"}

class ModSystemForm(forms.ModelForm):
    type = forms.ModelChoiceField(queryset=SystemType.objects.all().order_by('name'),widget=forms.Select(attrs={'class': 'select'}))
    area = forms.ModelChoiceField(queryset=Area.objects.all().order_by('name'), widget=forms.Select(attrs={'class': 'select'}))
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New system name'}))
    admin = forms.CharField(required=False,max_length=50,widget=forms.TextInput(attrs={'class': 'validation', 'type': 'username', 'placeholder': 'System Admin username'}))
    password = forms.CharField(required=False,max_length=50,widget=forms.PasswordInput(attrs={'class': 'validation', 'type': 'password', 'placeholder': 'System Admin password','style':'max-width:220px'}))

    def clean_password(self):
   
        try:
            system = self.instance
        except System.DoesNotExist:
            system = None

        current_password = encrypt_util.decrypt(system.password)    
        new_password = self.cleaned_data['password']

        if new_password == "":
            return current_password
        else:
            return new_password

    class Meta:
        model = System
        fields = ['type', 'area', 'name','admin','password']
        labels = {"type": "System Type", "area": "Area", "name": "Name","admin":"Admin","password":"Password"}

class AddAreaForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(queryset=AMSUser.objects.all().order_by('username'),blank=True, required=False,  widget=forms.SelectMultiple(attrs={'class': 'select'}))
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New system name'}))

    class Meta:
        model = Area
        fields = ['users', 'name',]
        labels = { "users": "Users", "name": "Name"}

class AddSystemTypeForm(forms.ModelForm):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New system name'}))

    class Meta:
        model = SystemType
        fields = ['name',]
        labels = { "name": "Name"}

class AddAccountForm(forms.ModelForm):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New account name'}))
    systems = forms.ModelMultipleChoiceField(queryset=System.objects.all().order_by('name'), widget=forms.SelectMultiple(attrs={'class': 'select'}))
    user = forms.ModelChoiceField(queryset=AMSUser.objects.all().order_by('username'), widget=forms.Select(attrs={'class': 'select'}))
    is_functional_user = forms.ChoiceField(choices=[(False, 'No'),(True, 'Yes')], widget=forms.Select(attrs={'class': 'select'}))
    class Meta:
        model = Account
        fields = ['name','user', 'systems','is_functional_user']
        labels = { 'name': 'Account name', 'is_functional_user' : 'Is this functional user?', 'user':'Create for User:', 'systems':'Systems on which account will be added'}

class AddApproverForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=AMSUser.objects.exclude(approver__isnull=False), widget=forms.Select(attrs={'class': 'select'}))
    area = forms.ModelMultipleChoiceField(queryset=Area.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select'}))
    
    class Meta:
        model = Approver
        fields = ['user', 'area']
        labels = { "user": "User",'area':"Choose area(s):"}

class ManageApproverForm(forms.ModelForm):
    area = forms.ModelMultipleChoiceField(queryset=Area.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select'}))
    
    class Meta:
        model = Approver
        fields = ['area']
        labels = {'area':"Choose area(s):"}

class OrderAccountStepOne(forms.Form):
    
    system_type = forms.ModelChoiceField(label='System Type',queryset=SystemType.objects.all().order_by('name'),  widget=forms.Select(attrs={'class': 'select'}))
    area = forms.ModelChoiceField(label='Area in which system is provided',queryset=Area.objects.all().order_by('name'), widget=forms.Select(attrs={'class': 'select'}))
    is_functional_user = forms.ChoiceField(label='Is this functional user', choices=[(False, 'No'),(True, 'Yes')], widget=forms.Select(attrs={'class': 'select'}))

class OrderAccountStepTwo(forms.Form):
    alphanumeric_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_.-]*$',
        message='Account name must be alphanumeric, and may contain underscores, dashes, and dots.',
        code='invalid_account_name'
    )
    account_name  = forms.CharField(label='Account Name', max_length=100, validators=[alphanumeric_validator], widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New account name'}))
    user = forms.ModelChoiceField(label='Account owner',queryset=AMSUser.objects.all().order_by('username'), widget=forms.Select(attrs={'class': 'select'}))
    account_profile= forms.ModelChoiceField(label='Account profile',queryset=ENMUserProfile.objects.all(), widget=forms.Select(attrs={'class': 'select'}))
        
    def clean_user(self):
        name = self.cleaned_data.get('account_name', '')
        user = self.cleaned_data['user']
        try:
            account = Account.objects.get(name = name )
        except Account.DoesNotExist:
            account = None
            return user
        if account.user.username != user.username:
            raise ValidationError("This functional user already exists and assigned to: "+ account.user.username )

        return user
    
class OrderAccountStepThree(forms.Form):
    systems = forms.ModelMultipleChoiceField(label='System Name',queryset=System.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select'}))
    def __init__(self, *args, **kwargs):
        initial_systems = kwargs.pop('initial_systems', [])
        super(OrderAccountStepThree, self).__init__(*args, **kwargs)

        # Set initial values for the 'systems' field
        self.fields['systems'].initial = initial_systems


class OrderAccountStepFour(forms.Form):
    # Define the summary field with a Textarea widget and readonly attribute
    summary = forms.CharField(widget=forms.Textarea(attrs={'readonly': 'readonly'}), label='Summary')

    def clean_summary(self):
        # Retrieve the cleaned summary data
        summary = self.cleaned_data['summary']
        
        # Perform any additional validation or transformation here if needed
        # For example, you might want to ensure the summary is not empty
        if not summary:
            raise forms.ValidationError("Summary cannot be empty.")
        
        return summary
    
    
class AddENMProfileForm(forms.ModelForm):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New profile name'}))
    schema = schema = forms.ModelMultipleChoiceField(label='ENM Role',queryset=ENMRole.objects.all(),  widget=forms.SelectMultiple(attrs={'class': 'select'}))
    
    class Meta:
        model = ENMUserProfile
        fields = ['name', 'schema']
        labels = { "name": "Profile name",'schema':"Schema:"}

class AddEICProfileForm(forms.ModelForm):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New profile name'}))
    schema = forms.ModelMultipleChoiceField(label='EIC Role',queryset=EICRole.objects.all(),  widget=forms.SelectMultiple(attrs={'class': 'select'}))
    
    class Meta:
        model = EICUserProfile
        fields = ['name', 'schema']
        labels = { "name": "Profile name",'schema':"Schema:"}

class AddEOProfileForm(forms.ModelForm):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New profile name'}))
    schema = forms.ModelMultipleChoiceField(label='EO Role',queryset=EORole.objects.all(),  widget=forms.SelectMultiple(attrs={'class': 'select'}))
    
    class Meta:
        model = EOUserProfile
        fields = ['name', 'schema']
        labels = { "name": "Profile name",'schema':"Schema:"}

class EnmResetPasswordForm(forms.Form):
    user = forms.ModelMultipleChoiceField(queryset=Account.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select'}))
    #user = forms.ModelChoiceField(label='Account owner',queryset=ENMUser.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select'}))
    system = forms.ModelMultipleChoiceField(queryset=System.objects.all(),  widget=forms.SelectMultiple(attrs={'class': 'select'})) 

class AddENMRoleForm(forms.ModelForm):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New role name'}))

    class Meta:
        model = ENMRole
        fields = ['name',]
        labels = { "name": "Role Name"}

class AddEORoleForm(forms.ModelForm):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New role name'}))    
    class Meta:
        model = EORole
        fields = ['name',]
        labels = { "name": "Role Name"}

class AddEICRoleForm(forms.ModelForm):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': 'with-icon', 'type': 'text', 'placeholder': 'New role name'}))    
    class Meta:
        model = EICRole
        fields = ['name',]
        labels = { "name": "Role Name"}