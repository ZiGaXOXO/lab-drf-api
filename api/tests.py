from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Todo
from django.urls import reverse

User = get_user_model()

class TodoAPITestCase(APITestCase):
    def setUp(self):
        # Создание пользователя и токена
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        # Клиент с авторизацией
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        # Создание несколько задач
        Todo.objects.create(title='Task 1', description='Desc1', completed=False, owner=self.user)
        Todo.objects.create(title='Task 2', description='Desc2', completed=True, owner=self.user)

    def test_get_todo_list(self):
        url = reverse('todo-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

    def test_create_todo_valid(self):
        url = reverse('todo-list-create')
        payload = {'title': 'New Task', 'description': 'New Desc', 'completed': False}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], 'New Task')

    def test_create_todo_invalid(self):
        url = reverse('todo-list-create')
        # Нет поля title
        payload = {'description': 'No title'}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json())

    def test_get_todo_detail(self):
        todo = Todo.objects.first()
        url = reverse('todo-detail', args=[todo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], todo.id)

    def test_update_todo_owner(self):
        todo = Todo.objects.first()
        url = reverse('todo-detail', args=[todo.id])
        payload = {'title': 'Updated', 'description': 'Upd', 'completed': True}
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Updated')

    def test_update_todo_not_owner(self):
        # Создадание другого пользователя и задачи у него
        other = User.objects.create_user(username='other', password='pass')
        other_todo = Todo.objects.create(title='Other Task', description='', completed=False, owner=other)
        url = reverse('todo-detail', args=[other_todo.id])
        payload = {'title': 'X'}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_todo(self):
        todo = Todo.objects.first()
        url = reverse('todo-detail', args=[todo.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 404)

    def test_filter_completed(self):
        url = reverse('todo-list-create') + '?completed=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for item in response.json():
            self.assertTrue(item['completed'])
