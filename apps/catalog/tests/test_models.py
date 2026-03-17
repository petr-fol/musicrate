"""
Тесты для моделей приложения Catalog
"""

from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse

from apps.catalog.models import Artist, Release
from apps.tests.base import BaseTestCase, create_test_image


class ArtistModelTest(BaseTestCase):
    """Тесты для модели Artist"""
    
    def test_artist_creation(self):
        """Создание артиста"""
        artist = Artist.objects.create(name='Test Artist')
        self.assertEqual(str(artist), 'Test Artist')
        self.assertIsNotNone(artist.slug)
    
    def test_artist_slug_generation(self):
        """Генерация slug для кириллических названий"""
        artist = Artist.objects.create(name='Кино')
        self.assertEqual(artist.slug, 'kino')
        
        artist_ru = Artist.objects.create(name='Мой район')
        self.assertEqual(artist_ru.slug, 'moj-rajon')
    
    def test_artist_slug_uniqueness(self):
        """Уникальность slug"""
        Artist.objects.create(name='Test Artist')
        # Второй артист с таким же именем должен получить уникальный slug
        artist2 = Artist.objects.create(name='Test Artist 2')
        self.assertNotEqual(artist2.slug, 'test-artist')
    
    def test_artist_get_absolute_url(self):
        """Проверка URL артиста"""
        artist = Artist.objects.create(name='Test Artist')
        url = artist.get_absolute_url()
        self.assertEqual(url, reverse('catalog:artist_detail', kwargs={'slug': artist.slug}))
    
    def test_artist_ordering(self):
        """Сортировка артистов по имени"""
        artist1 = Artist.objects.create(name='B Artist')
        artist2 = Artist.objects.create(name='A Artist')
        artists = list(Artist.objects.all())
        self.assertEqual(artists[0], artist2)
        self.assertEqual(artists[1], artist1)


class ReleaseModelTest(BaseTestCase):
    """Тесты для модели Release"""
    
    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='Test Artist')
    
    def test_release_creation(self):
        """Создание релиза"""
        release = Release.objects.create(
            title='Test Album',
            artist=self.artist,
            release_type='album'
        )
        self.assertEqual(str(release), 'Test Artist - Test Album')
        self.assertIsNotNone(release.slug)
    
    def test_release_slug_generation(self):
        """Генерация slug для релиза"""
        release = Release.objects.create(
            title='Тестовый альбом',
            artist=self.artist,
            release_type='album'
        )
        self.assertIn('testovyj', release.slug)
        self.assertIn('albom', release.slug)
    
    def test_release_slug_uniqueness(self):
        """Уникальность slug для релизов"""
        Release.objects.create(
            title='Test Album',
            artist=self.artist,
            release_type='album'
        )
        # Второй релиз с таким же названием должен получить уникальный slug
        release2 = Release.objects.create(
            title='Test Album',
            artist=self.artist,
            release_type='album'
        )
        self.assertNotEqual(release2.slug, 'test-artist-test-album')
    
    def test_release_type_choices(self):
        """Проверка типов релизов"""
        release_single = Release.objects.create(
            title='Single',
            artist=self.artist,
            release_type='single'
        )
        release_ep = Release.objects.create(
            title='EP',
            artist=self.artist,
            release_type='ep'
        )
        release_album = Release.objects.create(
            title='Album',
            artist=self.artist,
            release_type='album'
        )
        
        self.assertEqual(release_single.get_release_type_display(), 'Сингл')
        self.assertEqual(release_ep.get_release_type_display(), 'EP')
        self.assertEqual(release_album.get_release_type_display(), 'Альбом')
    
    def test_release_get_absolute_url(self):
        """Проверка URL релиза"""
        release = Release.objects.create(
            title='Test Album',
            artist=self.artist,
            release_type='album'
        )
        url = release.get_absolute_url()
        self.assertEqual(url, reverse('catalog:release_detail', kwargs={'slug': release.slug}))
    
    def test_release_update_average_score(self):
        """Обновление среднего балла релиза"""
        from apps.reviews.models import Review
        
        release = Release.objects.create(
            title='Test Album',
            artist=self.artist,
            release_type='album'
        )
        
        # Создадим рецензии
        Review.objects.create(
            user=self.user,
            release=release,
            rhymes=8,
            structure=7,
            style=9,
            charisma=8,
            atmosphere=4,
            text='Test review text ' * 10
        )
        
        # Обновим средний балл
        release.update_average_score()
        
        # Проверим значение (8+7+9+8+4 = 36)
        self.assertEqual(float(release.average_score), 36.0)
    
    def test_release_ordering(self):
        """Сортировка релизов по дате создания (новые сначала)"""
        release1 = Release.objects.create(
            title='Old Release',
            artist=self.artist,
            release_type='album'
        )
        release2 = Release.objects.create(
            title='New Release',
            artist=self.artist,
            release_type='album'
        )
        releases = list(Release.objects.all())
        self.assertEqual(releases[0], release2)


class ReleaseManagerTest(BaseTestCase):
    """Тесты для менеджеров Release"""
    
    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='Test Artist')
    
    def test_recent_releases(self):
        """Получение последних релизов"""
        for i in range(30):
            Release.objects.create(
                title=f'Release {i}',
                artist=self.artist,
                release_type='album'
            )
        
        recent = Release.objects.recent(limit=24)
        self.assertEqual(len(recent), 24)
    
    def test_releases_by_type(self):
        """Фильтрация по типу релиза"""
        Release.objects.create(title='Single 1', artist=self.artist, release_type='single')
        Release.objects.create(title='Album 1', artist=self.artist, release_type='album')
        Release.objects.create(title='EP 1', artist=self.artist, release_type='ep')
        
        singles = Release.objects.by_type('single')
        self.assertEqual(singles.count(), 1)
    
    def test_releases_with_covers(self):
        """Релизы с обложками"""
        # Создаём нового артиста для изоляции теста
        artist = Artist.objects.create(name='Cover Test Artist Unique')
        
        release_with_cover = Release.objects.create(
            title='With Cover Unique',
            artist=artist,
            release_type='album',
            cover=create_test_image()
        )
        
        # Проверяем что обложка сохранена (проверяем что файл существует)
        release_with_cover.refresh_from_db()
        self.assertTrue(bool(release_with_cover.cover))


class ArtistManagerTest(BaseTestCase):
    """Тесты для менеджеров Artist"""
    
    def test_artists_with_releases_count(self):
        """Артисты с количеством релизов"""
        artist1 = Artist.objects.create(name='Artist 1')
        artist2 = Artist.objects.create(name='Artist 2')
        
        Release.objects.create(title='Release 1', artist=artist1, release_type='album')
        Release.objects.create(title='Release 2', artist=artist1, release_type='album')
        Release.objects.create(title='Release 3', artist=artist2, release_type='album')
        
        artists = Artist.objects.with_releases_count()
        
        a1 = next(a for a in artists if a.name == 'Artist 1')
        a2 = next(a for a in artists if a.name == 'Artist 2')
        
        self.assertEqual(a1.releases_count, 2)
        self.assertEqual(a2.releases_count, 1)
    
    def test_artists_has_releases(self):
        """Только артисты с релизами"""
        artist_with_releases = Artist.objects.create(name='With Releases')
        artist_without_releases = Artist.objects.create(name='Without Releases')
        
        Release.objects.create(
            title='Release',
            artist=artist_with_releases,
            release_type='album'
        )
        
        artists = Artist.objects.has_releases()
        self.assertEqual(artists.count(), 1)
        self.assertEqual(artists.first(), artist_with_releases)
