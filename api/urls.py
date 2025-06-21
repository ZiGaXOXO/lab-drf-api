from django.urls import path
from .views import *

urlpatterns = [
    path('hello/', HelloAPIView.as_view(), name='hello'),
    path('todos/', TodoListCreateAPIView.as_view(), name='todo-list-create'),
    path('todos/<int:pk>/', TodoDetailAPIView.as_view(), name='todo-detail'),
]
