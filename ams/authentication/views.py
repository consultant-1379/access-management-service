from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate,logout, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home:index')
            else:
                form.add_error(None, 'Invalid login credentials')
                messages.error(request, 'Invalid login credentials')
    else:
        form = LoginForm()

    return render(request, 'authentication/login.page.tmpl.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home:index')
