from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

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
                # Проверяем, является ли пользователь администратором
                if user.is_staff:
                    return redirect('lab2:user_list')  # Перенаправляем администраторов на список пользователей
                else:
                    return redirect('lab2:profile')  # Обычных пользователей - на профиль
    else:
        form = AuthenticationForm()
    return render(request, 'lab2/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('lab2:login')

@login_required
def profile_view(request):
    return render(request, 'lab2/profile.html', {'user': request.user})

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def user_list_view(request):
    user_list = User.objects.all().order_by('username')
    paginator = Paginator(user_list, 10)  # 10 пользователей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'lab2/user_list.html', {'page_obj': page_obj})