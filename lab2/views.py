from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация успешна. Пожалуйста, войдите.")
            return redirect('lab2:login')
    else:
        form = RegistrationForm()
    return render(request, 'lab2/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('lab2:profile')
    else:
        form = AuthenticationForm()
    return render(request, 'lab2/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('lab2:login')