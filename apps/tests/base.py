"""
Базовые классы и утилиты для тестирования
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для всех тестов"""
    
    @classmethod
    def setUpTestData(cls):
        """Настройка данных для всех тестов"""
        super().setUpTestData()
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cls.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
    
    def setUp(self):
        """Настройка для каждого теста"""
        self.client = Client()


class AuthenticatedTestCase(BaseTestCase):
    """Базовый класс для тестов с авторизованным пользователем"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass123')


def create_test_image():
    """Создает тестовое изображение"""
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10',
        content_type='image/jpeg'
    )
