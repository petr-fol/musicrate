"""
Тесты для представлений приложения Catalog
"""

from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.catalog.models import Artist, Release
from apps.tests.base import BaseTestCase, AuthenticatedTestCase

User = get_user_model()


class IndexViewTest(BaseTestCase):
    """Тесты для главной страницы"""
    
    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='Test Artist')
    
    def test_index_view_status_code(self):
        """Проверка статуса главной страницы"""
        response = self.client.get(reverse('catalog:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_index_view_template(self):
        """Проверка использования шаблона"""
        response = self.client.get(reverse('catalog:index'))
        self.assertTemplateUsed(response, 'catalog/index.html')
    
    def test_index_view_shows_releases(self):
        """Проверка отображения релизов"""
        Release.objects.create(
            title='Test Release',
            artist=self.artist,
            release_type='album'
        )
        
        response = self.client.get(reverse('catalog:index'))
        self.assertContains(response, 'Test Release')
    
    def test_index_view_recommendations_for_authenticated(self):
        """Проверка рекомендаций для авторизованных"""
        self.client.login(username='testuser', password='testpass123')
        
        # Создадим релиз
        release = Release.objects.create(
            title='Recommended',
            artist=self.artist,
            release_type='album'
        )
        
        response = self.client.get(reverse('catalog:index'))
        self.assertEqual(response.status_code, 200)


class ReleaseDetailViewTest(BaseTestCase):
    """Тесты для страницы релиза"""
    
    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='Test Artist')
        self.release = Release.objects.create(
            title='Test Album',
            artist=self.artist,
            release_type='album'
        )
    
    def test_release_detail_status_code(self):
        """Проверка статуса страницы релиза"""
        url = reverse('catalog:release_detail', kwargs={'slug': self.release.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_release_detail_template(self):
        """Проверка шаблона"""
        url = reverse('catalog:release_detail', kwargs={'slug': self.release.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'catalog/release_detail.html')
    
    def test_release_detail_shows_correct_release(self):
        """Проверка отображения правильного релиза"""
        url = reverse('catalog:release_detail', kwargs={'slug': self.release.slug})
        response = self.client.get(url)
        self.assertContains(response, 'Test Album')
        self.assertContains(response, 'Test Artist')
    
    def test_release_detail_404(self):
        """Проверка 404 для несуществующего релиза"""
        url = reverse('catalog:release_detail', kwargs={'slug': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class SearchViewTest(BaseTestCase):
    """Тесты для поиска"""
    
    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='Test Artist')
        self.release = Release.objects.create(
            title='Test Release',
            artist=self.artist,
            release_type='album'
        )
        self.user = User.objects.create_user(
            username='searchuser',
            password='pass123'
        )
    
    def test_search_view_status_code(self):
        """Проверка статуса страницы поиска"""
        response = self.client.get(reverse('catalog:api_search'))
        self.assertEqual(response.status_code, 200)
    
    def test_search_view_results(self):
        """Проверка результатов поиска"""
        response = self.client.get(reverse('catalog:api_search'), {'q': 'Test'})
        self.assertContains(response, 'Test Release')
        self.assertContains(response, 'Test Artist')
    
    def test_search_view_no_results(self):
        """Поиск без результатов"""
        response = self.client.get(reverse('catalog:api_search'), {'q': 'NonExistent'})
        self.assertNotContains(response, 'Test Release')
    
    def test_search_by_type_releases(self):
        """Поиск только релизов"""
        response = self.client.get(reverse('catalog:api_search'), {
            'q': 'Test',
            'type': 'releases'
        })
        self.assertContains(response, 'Test Release')
    
    def test_search_by_type_artists(self):
        """Поиск только артистов"""
        response = self.client.get(reverse('catalog:api_search'), {
            'q': 'Test',
            'type': 'artists'
        })
        self.assertContains(response, 'Test Artist')
    
    def test_search_by_type_users(self):
        """Поиск пользователей"""
        response = self.client.get(reverse('catalog:api_search'), {
            'q': 'searchuser',
            'type': 'users'
        })
        self.assertContains(response, 'searchuser')


class ArtistDetailViewTest(BaseTestCase):
    """Тесты для страницы артиста"""
    
    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='Test Artist')
    
    def test_artist_detail_status_code(self):
        """Проверка статуса страницы артиста"""
        url = reverse('catalog:artist_detail', kwargs={'slug': self.artist.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_artist_detail_template(self):
        """Проверка шаблона"""
        url = reverse('catalog:artist_detail', kwargs={'slug': self.artist.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'catalog/artist_detail.html')
    
    def test_artist_detail_shows_releases(self):
        """Проверка отображения релизов артиста"""
        Release.objects.create(
            title='Test Album',
            artist=self.artist,
            release_type='album'
        )
        
        url = reverse('catalog:artist_detail', kwargs={'slug': self.artist.slug})
        response = self.client.get(url)
        self.assertContains(response, 'Test Album')
    
    def test_artist_detail_404(self):
        """Проверка 404 для несуществующего артиста"""
        url = reverse('catalog:artist_detail', kwargs={'slug': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ImportReleaseViewTest(AuthenticatedTestCase):
    """Тесты для импорта релиза"""
    
    def test_import_requires_login(self):
        """Импорт требует авторизации"""
        self.client.logout()
        url = reverse('catalog:import_release', kwargs={'yandex_id': '123'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login/'))
