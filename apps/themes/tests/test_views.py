"""
Тесты для представлений приложения Themes
"""

from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.themes.models import Theme, ThemePreference
from apps.tests.base import BaseTestCase, AuthenticatedTestCase

User = get_user_model()


class SetThemeViewTest(AuthenticatedTestCase):
    """Тесты для переключения тем"""
    
    def setUp(self):
        super().setUp()
        self.theme = Theme.objects.create(
            name='Test Theme',
            slug='test-theme',
            theme_type='dark'
        )
        self.url = reverse('themes:set_theme')
    
    def test_set_theme_requires_login(self):
        """Переключение темы требует авторизации"""
        self.client.logout()
        response = self.client.post(self.url, {'theme_slug': self.theme.slug})
        self.assertEqual(response.status_code, 302)
    
    def test_set_theme_post_valid(self):
        """POST запрос с валидными данными"""
        response = self.client.post(self.url, {'theme_slug': self.theme.slug})
        
        self.assertEqual(response.status_code, 302)
        
        preference = ThemePreference.objects.get(user=self.user)
        self.assertEqual(preference.theme, self.theme)
    
    def test_set_theme_invalid_slug(self):
        """POST запрос с несуществующим slug"""
        response = self.client.post(self.url, {'theme_slug': 'nonexistent'})
        
        self.assertEqual(response.status_code, 404)
    
    def test_set_theme_htmx_request(self):
        """HTMX запрос"""
        response = self.client.post(
            self.url,
            {'theme_slug': self.theme.slug},
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'themes/partials/theme_switcher.html')


class AvailableThemesViewTest(BaseTestCase):
    """Тесты для получения доступных тем"""
    
    def setUp(self):
        super().setUp()
        Theme.objects.create(
            name='Active Theme',
            slug='active-theme',
            is_active=True
        )
        Theme.objects.create(
            name='Inactive Theme',
            slug='inactive-theme',
            is_active=False
        )
        self.url = reverse('themes:available_themes')
    
    def test_available_themes_status_code(self):
        """Проверка статуса"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_available_themes_returns_json(self):
        """Возвращает JSON"""
        response = self.client.get(self.url)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_available_themes_only_active(self):
        """Только активные темы"""
        response = self.client.get(self.url)
        data = response.json()
        
        theme_slugs = [t['slug'] for t in data['themes']]
        self.assertIn('active-theme', theme_slugs)
        self.assertNotIn('inactive-theme', theme_slugs)
    
    def test_available_themes_structure(self):
        """Структура ответа"""
        response = self.client.get(self.url)
        data = response.json()
        
        self.assertIn('themes', data)
        self.assertIsInstance(data['themes'], list)
        
        if data['themes']:
            theme = data['themes'][0]
            self.assertIn('name', theme)
            self.assertIn('slug', theme)
            self.assertIn('theme_type', theme)
            self.assertIn('css_variables', theme)
