from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from api.models import Todo
from .models import Comment
from django.conf import settings
from .decorators import group_required
import os


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

@login_required
def session_demo(request):
    # Пример счётчика: сколько раз пользователь заходил на эту страницу
    visits = request.session.get('visits', 0)
    visits += 1
    request.session['visits'] = visits

    return render(request, 'lab2/session_demo.html', {'visits': visits})

@login_required
def session_clear(request):
    try:
        del request.session['visits']
    except KeyError:
        pass
    return redirect('lab2:session_demo')

def search_view(request):
    form = SearchForm(request.GET)
    if not form.is_valid():
        # вернуть ошибки в шаблон или JSON
        return render(request, 'lab2/search.html', {'form': form})
    q = form.cleaned_data['q']
    page = form.cleaned_data.get('page') or 1
    # Выполнить поиск, например, по модели Todo:

    todos = Todo.objects.filter(title__icontains=q)
    paginator = Paginator(todos, 10)
    page_obj = paginator.get_page(page)
    return render(request, 'lab2/search.html', {'form': form, 'page_obj': page_obj, 'q': q})


@login_required
def comment_create_view(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            cleaned_content = form.cleaned_data['content']
            # Создаем комментарий
            Comment.objects.create(
                user=request.user,
                content=cleaned_content
            )
            return redirect('lab2:comment_list')
    else:
        form = CommentForm()

    return render(request, 'lab2/comment_form.html', {'form': form})


def comment_list_view(request):
    comments = Comment.objects.all().order_by('-created_at')
    return render(request, 'lab2/comment_list.html', {'comments': comments})

def clean_file(self):
    f = self.cleaned_data['file']
    if f.size > 5*1024*1024:
        raise ValidationError("Слишком большой файл (>5MB)")
    if not f.content_type in ['image/jpeg', 'image/png']:
        raise ValidationError("Только JPEG/PNG разрешены")
    return f

@login_required
def upload_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            user_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', request.user.username)
            os.makedirs(user_folder, exist_ok=True)
            filepath = os.path.join(user_folder, uploaded_file.name)
            with open(filepath, 'wb+') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)
            messages.success(request, "Файл загружен")
            return redirect('lab2:upload')
    else:
        form = FileUploadForm()
    return render(request, 'lab2/upload.html', {'form': form})


@group_required('managers')
def manager_dashboard(request):
    # только пользователи из группы 'managers'
    return render(request, 'lab2/manager_dashboard.html')
