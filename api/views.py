from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import TodoSerializer
from .models import Todo
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny

class TodoListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        todos = Todo.objects.all()

        # Фильтрация по completed
        completed = request.GET.get('completed')
        if completed is not None:
            val = completed.lower()
            if val in ['true', '1', 'yes']:
                todos = todos.filter(completed=True)
            elif val in ['false', '0', 'no']:
                todos = todos.filter(completed=False)
        # Поиск по title (icontains)
        search = request.GET.get('search')
        if search:
            todos = todos.filter(title__icontains=search)

        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():

            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HelloAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        data = {'message': 'Hello, world!'}
        return Response(data)

    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': f'Hello, {name}!'})

class TodoDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Todo, pk=pk)

    def get(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data)

    def put(self, request, pk):
        todo = self.get_object(pk)
        if todo.owner != request.user:
            return Response({'detail': 'Не авторизованы для изменения этой задачи'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TodoSerializer(todo, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(owner=request.user)
        return Response(serializer.data)

    def patch(self, request, pk):
        todo = self.get_object(pk)
        if todo.owner != request.user:
            return Response({'detail': 'Не авторизованы для изменения этой задачи'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TodoSerializer(todo, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(owner=request.user)
        return Response(serializer.data)

    def delete(self, request, pk):
        todo = self.get_object(pk)
        if todo.owner != request.user:
            return Response({'detail': 'Не авторизованы для удаления этой задачи'}, status=status.HTTP_403_FORBIDDEN)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
