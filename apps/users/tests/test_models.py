"""
Тесты для модели User
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.tests.base import BaseTestCase

User = get_user_model()


class UserModelTest(BaseTestCase):
    """Тесты для модели User"""
    
    def test_user_creation(self):
        """Создание пользователя"""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='pass123'
        )
        
        self.assertEqual(str(user), 'newuser')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_superuser_creation(self):
        """Создание суперпользователя"""
        admin = User.objects.create_superuser(
            username='superadmin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
    
    def test_user_get_display_name_with_names(self):
        """Получение отображаемого имени с именем и фамилией"""
        user = User.objects.create_user(
            username='displayuser',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.get_display_name(), 'John Doe')
    
    def test_user_get_display_name_without_names(self):
        """Получение отображаемого имени без имени и фамилии"""
        user = User.objects.create_user(
            username='displayuser2'
        )
        
        self.assertEqual(user.get_display_name(), 'displayuser2')
    
    def test_user_points_default(self):
        """Очки репутации по умолчанию"""
        user = User.objects.create_user(
            username='newuser',
            password='pass123'
        )
        
        self.assertEqual(user.points, 0)
    
    def test_user_points_update(self):
        """Обновление очков репутации"""
        user = User.objects.create_user(
            username='pointsuser',
            password='pass123'
        )
        
        user.points = 100
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.points, 100)
    
    def test_user_ordering(self):
        """Сортировка пользователей по username"""
        # Создаём пользователей с уникальными именами
        user1 = User.objects.create_user(username='zuser_unique', password='pass')
        user2 = User.objects.create_user(username='auser_unique', password='pass')
        
        users = list(User.objects.all())
        # Проверяем что пользователи отсортированы по username
        usernames = [u.username for u in users]
        self.assertEqual(usernames, sorted(usernames))


class UserProfileViewTest(BaseTestCase):
    """Тесты для страницы профиля"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('users:profile', kwargs={'username': self.user.username})
    
    def test_profile_status_code(self):
        """Проверка статуса страницы профиля"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_profile_template(self):
        """Проверка шаблона"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'users/profile.html')
    
    def test_profile_shows_user_info(self):
        """Проверка отображения информации о пользователе"""
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)
    
    def test_profile_404(self):
        """Проверка 404 для несуществующего пользователя"""
        url = reverse('users:profile', kwargs={'username': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
