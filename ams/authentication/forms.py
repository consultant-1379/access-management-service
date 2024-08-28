from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AMSUser

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'id': 'username' , 'class':'validation'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'password','class':'validation'}))

class AMSUserCreationForm(UserCreationForm):
    class Meta:
        model = AMSUser
        fields = '__all__'