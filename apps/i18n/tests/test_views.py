"""
Тесты для интернационализации (i18n)
"""

from django.urls import reverse
from django.test import Client
from django.conf import settings

from apps.tests.base import BaseTestCase


class LanguageSwitcherTest(BaseTestCase):
    """Тесты для переключателя языков"""
    
    def setUp(self):
        super().setUp()
        self.url = reverse('i18n:set_language')
    
    def test_set_language_requires_post(self):
        """Переключение языка требует POST запроса"""
        response = self.client.get(self.url, {'language': 'en'})
        self.assertEqual(response.status_code, 405)
    
    def test_set_language_valid_language(self):
        """Переключение на валидный язык"""
        response = self.client.post(self.url, {
            'language': 'en',
            'next': '/'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies['django_language'].value, 'en')
    
    def test_set_language_invalid_language(self):
        """Переключение на невалидный язык"""
        response = self.client.post(self.url, {
            'language': 'invalid',
            'next': '/'
        })
        
        # Должен перенаправить на referer или '/'
        self.assertEqual(response.status_code, 302)
    
    def test_set_language_ru(self):
        """Переключение на русский"""
        response = self.client.post(self.url, {
            'language': 'ru',
            'next': '/'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies['django_language'].value, 'ru')
    
    def test_set_language_kk(self):
        """Переключение на казахский"""
        response = self.client.post(self.url, {
            'language': 'kk',
            'next': '/'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies['django_language'].value, 'kk')
    
    def test_set_language_htmx_request(self):
        """POST запрос для переключения языка"""
        response = self.client.post(
            self.url,
            {'language': 'en', 'next': '/'},
        )

        # Должен перенаправить и установить cookie
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies['django_language'].value, 'en')


class LanguageConfigurationTest(BaseTestCase):
    """Тесты для конфигурации языков"""
    
    def test_languages_configured(self):
        """Языки настроены в settings"""
        self.assertEqual(len(settings.LANGUAGES), 3)
        
        lang_codes = [lang[0] for lang in settings.LANGUAGES]
        self.assertIn('ru', lang_codes)
        self.assertIn('en', lang_codes)
        self.assertIn('kk', lang_codes)
    
    def test_locale_paths_configured(self):
        """LOCALE_PATHS настроен"""
        self.assertIn('locale', str(settings.LOCALE_PATHS[0]))
    
    def test_use_i18n_enabled(self):
        """USE_I18N включён"""
        self.assertTrue(settings.USE_I18N)


class LanguageContextProcessorTest(BaseTestCase):
    """Тесты для контекстного процессора языков"""
    
    def test_language_context_available(self):
        """Контекст языка доступен в шаблонах"""
        response = self.client.get('/')
        
        # Проверяем что контекстный процессор работает
        self.assertIn('current_language', response.context)
        self.assertIn('available_languages', response.context)
    
    def test_available_languages_in_context(self):
        """Доступные языки в контексте"""
        response = self.client.get('/')
        
        languages = response.context['available_languages']
        self.assertEqual(len(languages), 3)
