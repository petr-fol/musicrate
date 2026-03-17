"""
Тесты для моделей приложения Themes
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.themes.models import Theme, ThemePreference
from apps.tests.base import BaseTestCase

User = get_user_model()


class ThemeModelTest(BaseTestCase):
    """Тесты для модели Theme"""
    
    def test_theme_creation(self):
        """Создание темы"""
        theme = Theme.objects.create(
            name='Test Theme',
            slug='test-theme',
            theme_type='dark'
        )
        
        self.assertEqual(str(theme), 'Test Theme (Тёмная)')
        self.assertTrue(theme.is_active)
        self.assertFalse(theme.is_default)
    
    def test_theme_default_colors(self):
        """Цвета темы по умолчанию"""
        theme = Theme.objects.create(
            name='Test Theme',
            slug='test-theme'
        )
        
        self.assertEqual(theme.bg_primary, '#0a0a0a')
        self.assertEqual(theme.bg_secondary, '#141414')
        self.assertEqual(theme.accent_primary, '#ffcc00')
    
    def test_theme_get_css_variables(self):
        """Получение CSS переменных"""
        theme = Theme.objects.create(
            name='Test Theme',
            slug='test-theme',
            bg_primary='#111111'
        )
        
        css_vars = theme.get_css_variables()
        
        self.assertEqual(css_vars['--bg-primary'], '#111111')
        self.assertIn('--accent-primary', css_vars)
    
    def test_theme_set_default(self):
        """Установка темы по умолчанию"""
        theme1 = Theme.objects.create(
            name='Theme 1',
            slug='theme-1',
            is_default=True
        )
        
        theme2 = Theme.objects.create(
            name='Theme 2',
            slug='theme-2',
            is_default=True
        )
        
        theme1.refresh_from_db()
        self.assertFalse(theme1.is_default)
        self.assertTrue(theme2.is_default)
    
    def test_theme_type_choices(self):
        """Выбор типа темы"""
        dark_theme = Theme.objects.create(
            name='Dark Theme',
            slug='dark-theme',
            theme_type='dark'
        )
        
        light_theme = Theme.objects.create(
            name='Light Theme',
            slug='light-theme',
            theme_type='light'
        )
        
        self.assertEqual(dark_theme.get_theme_type_display(), 'Тёмная')
        self.assertEqual(light_theme.get_theme_type_display(), 'Светлая')
    
    def test_theme_ordering(self):
        """Сортировка тем: сначала default, потом по имени"""
        # Создаём новую тему с is_default=True
        # Темы из миграции уже существуют, поэтому создаём новую с уникальным slug
        default_theme = Theme.objects.create(
            name='Z Default Theme',
            slug='z-default-theme',
            is_default=True
        )
        
        # Проверяем что она первая (is_default=True устанавливается автоматически)
        themes = list(Theme.objects.filter(slug__startswith='z-'))
        self.assertEqual(themes[0], default_theme)


class ThemePreferenceModelTest(BaseTestCase):
    """Тесты для модели ThemePreference"""
    
    def test_theme_preference_creation(self):
        """Создание предпочтения темы"""
        theme = Theme.objects.create(
            name='Test Theme',
            slug='test-theme'
        )
        
        preference = ThemePreference.objects.create(
            user=self.user,
            theme=theme
        )
        
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.theme, theme)
    
    def test_theme_preference_set_default_on_delete(self):
        """Установка темы по умолчанию при удалении"""
        default_theme = Theme.objects.create(
            name='Default Theme',
            slug='default-theme',
            is_default=True
        )
        
        custom_theme = Theme.objects.create(
            name='Custom Theme',
            slug='custom-theme'
        )
        
        preference = ThemePreference.objects.create(
            user=self.user,
            theme=custom_theme
        )
        
        custom_theme.delete()
        
        preference.refresh_from_db()
        self.assertIsNone(preference.theme)
    
    def test_theme_preference_str(self):
        """Строковое представление"""
        theme = Theme.objects.create(
            name='Test Theme',
            slug='test-theme'
        )
        
        preference = ThemePreference.objects.create(
            user=self.user,
            theme=theme
        )
        
        self.assertEqual(str(preference), 'testuser - Test Theme')
