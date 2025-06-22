from django.urls import path
from . import views

app_name = 'lab2'
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.user_list_view, name='user_list'),
    path('session/', views.session_demo, name='session_demo'),
    path('session/clear/', views.session_clear, name='session_clear'),
    path('search/', views.search_view, name='search'),
]
