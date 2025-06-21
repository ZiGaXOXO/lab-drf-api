from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import TodoSerializer
from .models import Todo

class HelloAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Приветственное сообщение",
        operation_description="Возвращает 'Hello, world!' в формате JSON.",
        responses={200: openapi.Response('OK', examples={"application/json": {"message": "Hello, world!"}})}
    )
    def get(self, request):
        return Response({'message': 'Hello, world!'})

    @swagger_auto_schema(
        operation_summary="Приветствие по имени",
        operation_description="Ожидает параметр 'name' в теле запроса и возвращает персональное сообщение.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={"name": openapi.Schema(type=openapi.TYPE_STRING)}
        ),
        responses={
            200: openapi.Response('OK', examples={"application/json": {"message": "Hello, имя!"}}),
            400: openapi.Response('Ошибка', examples={"application/json": {"error": "Name is required"}})
        }
    )
    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': f'Hello, {name}!'})


class TodoListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Список задач",
        operation_description="Возвращает список задач с возможностью фильтрации по статусу (completed) и поиску по заголовку (search).",
        manual_parameters=[
            openapi.Parameter('completed', openapi.IN_QUERY, description="true / false", type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, description="Поиск по заголовку", type=openapi.TYPE_STRING),
        ],
        responses={200: TodoSerializer(many=True)}
    )
    def get(self, request):
        todos = Todo.objects.all()
        completed = request.GET.get('completed')
        if completed is not None:
            val = completed.lower()
            if val in ['true', '1', 'yes']:
                todos = todos.filter(completed=True)
            elif val in ['false', '0', 'no']:
                todos = todos.filter(completed=False)
        search = request.GET.get('search')
        if search:
            todos = todos.filter(title__icontains=search)

        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Создание задачи",
        request_body=TodoSerializer,
        responses={
            201: TodoSerializer,
            400: "Ошибка валидации"
        }
    )
    def post(self, request):
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Todo, pk=pk)

    @swagger_auto_schema(
        operation_summary="Получить задачу по ID",
        responses={200: TodoSerializer, 404: "Не найдено"}
    )
    def get(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Полное обновление задачи",
        request_body=TodoSerializer,
        responses={200: TodoSerializer, 403: "Нет доступа", 400: "Ошибка валидации"}
    )
    def put(self, request, pk):
        todo = self.get_object(pk)
        if todo.owner != request.user:
            return Response({'detail': 'Не авторизованы для изменения этой задачи'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TodoSerializer(todo, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(owner=request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Частичное обновление задачи",
        request_body=TodoSerializer,
        responses={200: TodoSerializer, 403: "Нет доступа", 400: "Ошибка валидации"}
    )
    def patch(self, request, pk):
        todo = self.get_object(pk)
        if todo.owner != request.user:
            return Response({'detail': 'Не авторизованы для изменения этой задачи'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TodoSerializer(todo, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(owner=request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Удалить задачу",
        responses={204: "Удалено", 403: "Нет доступа", 404: "Не найдено"}
    )
    def delete(self, request, pk):
        todo = self.get_object(pk)
        if todo.owner != request.user:
            return Response({'detail': 'Не авторизованы для удаления этой задачи'}, status=status.HTTP_403_FORBIDDEN)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
