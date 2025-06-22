from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('lab2:register')
        self.login_url = reverse('lab2:login')
        self.profile_url = reverse('lab2:profile')
        # Пользователь для login-test
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'password_confirm': 'password123',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)
        # Проверяем, что пользователь создан:
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_logout(self):
        # Логин с корректными данными
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # редирект после логина
        # После логина client хранит сессию:
        response2 = self.client.get(self.profile_url)
        self.assertEqual(response2.status_code, 200)
        logout_url = reverse('lab2:logout')
        response3 = self.client.get(logout_url)
        self.assertEqual(response3.status_code, 302)
        response4 = self.client.get(self.profile_url)
        self.assertNotEqual(response4.status_code, 200)

    def test_profile_requires_login(self):
        # Без логина
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

class SessionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # создаём пользователя и логинимся
        self.user = User.objects.create_user(username='sessuser', password='pass')
        self.client.login(username='sessuser', password='pass')
        self.session_url = reverse('lab2:session_demo')
        self.clear_url = reverse('lab2:session_clear')

    def test_session_counter(self):
        # Первый визит
        response1 = self.client.get(self.session_url)
        self.assertContains(response1, "Вы посетили эту страницу 1")
        # Второй визит
        response2 = self.client.get(self.session_url)
        self.assertContains(response2, "Вы посетили эту страницу 2")
        # Очистка
        response3 = self.client.get(self.clear_url)
        # После очистки следующий визит снова 1
        response4 = self.client.get(self.session_url)
        self.assertContains(response4, "Вы посетили эту страницу 1")


class RequestCleaningTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Предположим, что у вас есть view search_view с именем 'lab2:search'
        self.search_url = reverse('lab2:search')
        # И upload_view с именем 'lab2:upload'
        self.user = User.objects.create_user(username='fileuser', password='pass')
        self.client.login(username='fileuser', password='pass')

    def test_search_invalid_params(self):
        # Отсутствует обязательный параметр q
        response = self.client.get(self.search_url, {})
        # Форма невалидна, возвращается status 200, но с ошибками в форме
        self.assertContains(response, "This field is required", status_code=200)
    def test_file_upload_validation(self):
        # Проверка ограничения типа/размера
        upload_url = reverse('lab2:upload')
        # Создадим заглушку файла большого размера
        from django.core.files.uploadedfile import SimpleUploadedFile
        # Предположим, ограничение 5MB, создадим файл 6MB:
        large_content = b'a' * (6 * 1024 * 1024)
        large_file = SimpleUploadedFile('large.txt', large_content, content_type='text/plain')
        response = self.client.post(upload_url, {'file': large_file})
        # Ожидаем, что форма вернёт ошибку в шаблоне
        self.assertContains(response, "Слишком большой файл", status_code=200)
