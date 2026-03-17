"""
Тесты для сервисов приложения Catalog
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.catalog.models import Artist, Release
from apps.catalog.services.recommendations import (
    get_user_recommendations,
    _calculate_artist_counts,
    _get_releases_from_artists,
)
from apps.tests.base import BaseTestCase

User = get_user_model()


class RecommendationServiceTest(BaseTestCase):
    """Тесты для системы рекомендаций"""
    
    def setUp(self):
        super().setUp()
        self.artist1 = Artist.objects.create(name='Artist 1')
        self.artist2 = Artist.objects.create(name='Artist 2')
        self.artist3 = Artist.objects.create(name='Artist 3')
    
    def test_get_recommendations_for_new_user(self):
        """Рекомендации для нового пользователя (без рецензий)"""
        # Создадим популярные релизы
        for i in range(5):
            Release.objects.create(
                title=f'Popular Release {i}',
                artist=self.artist1,
                release_type='album',
                average_score=40.0
            )
        
        recommendations = get_user_recommendations(self.user)
        
        # Должны вернуться популярные релизы
        self.assertGreater(len(recommendations), 0)
    
    def test_get_recommendations_based_on_preferences(self):
        """Рекомендации на основе предпочтений пользователя"""
        from apps.reviews.models import Review
        
        # Пользователь оценил несколько релизов artist1
        for i in range(3):
            release = Release.objects.create(
                title=f'Artist 1 Release {i}',
                artist=self.artist1,
                release_type='album'
            )
            Review.objects.create(
                user=self.user,
                release=release,
                rhymes=8,
                structure=8,
                style=8,
                charisma=8,
                atmosphere=4,
                text='Great release! ' * 10
            )
        
        # Создадим новый релиз от artist1
        new_release = Release.objects.create(
            title='New Artist 1 Release',
            artist=self.artist1,
            release_type='album'
        )
        
        recommendations = get_user_recommendations(self.user)
        
        # Новый релиз должен быть в рекомендациях
        recommended_ids = [r.id for r in recommendations]
        self.assertIn(new_release.id, recommended_ids)
    
    def test_get_recommendations_excludes_reviewed(self):
        """Рекомендации не включают оценённые релизы"""
        from apps.reviews.models import Review
        
        release = Release.objects.create(
            title='Reviewed Release',
            artist=self.artist1,
            release_type='album'
        )
        
        Review.objects.create(
            user=self.user,
            release=release,
            rhymes=8,
            structure=8,
            style=8,
            charisma=8,
            atmosphere=4,
            text='Test review ' * 10
        )
        
        recommendations = get_user_recommendations(self.user)
        
        # Оценённый релиз не должен быть в рекомендациях
        recommended_ids = [r.id for r in recommendations]
        self.assertNotIn(release.id, recommended_ids)
    
    def test_calculate_artist_counts(self):
        """Подсчёт количества рецензий по артистам"""
        from apps.reviews.models import Review
        
        release1 = Release.objects.create(
            title='Release 1',
            artist=self.artist1,
            release_type='album'
        )
        release2 = Release.objects.create(
            title='Release 2',
            artist=self.artist1,
            release_type='album'
        )
        release3 = Release.objects.create(
            title='Release 3',
            artist=self.artist2,
            release_type='album'
        )
        
        Review.objects.create(
            user=self.user,
            release=release1,
            rhymes=8, structure=8, style=8, charisma=8, atmosphere=4,
            text='Test ' * 10
        )
        Review.objects.create(
            user=self.user,
            release=release2,
            rhymes=8, structure=8, style=8, charisma=8, atmosphere=4,
            text='Test ' * 10
        )
        Review.objects.create(
            user=self.user,
            release=release3,
            rhymes=8, structure=8, style=8, charisma=8, atmosphere=4,
            text='Test ' * 10
        )
        
        user_reviews = self.user.reviews.all()
        artist_counts = _calculate_artist_counts(user_reviews)
        
        self.assertEqual(artist_counts[self.artist1.id], 2)
        self.assertEqual(artist_counts[self.artist2.id], 1)
    
    def test_get_releases_from_artists(self):
        """Получение релизов от указанных артистов"""
        release1 = Release.objects.create(
            title='Release 1',
            artist=self.artist1,
            release_type='album'
        )
        release2 = Release.objects.create(
            title='Release 2',
            artist=self.artist2,
            release_type='album'
        )
        
        releases = _get_releases_from_artists(
            [self.artist1.id],
            excluded_release_ids=[],
            limit=10
        )
        
        self.assertEqual(releases.count(), 1)
        self.assertEqual(releases.first(), release1)


class YandexMusicProviderTest(TestCase):
    """Тесты для YandexMusicProvider"""
    
    def test_provider_initialization_without_token(self):
        """Инициализация провайдера без токена"""
        from apps.catalog.services.yandex_music import YandexMusicProvider
        
        provider = YandexMusicProvider()
        self.assertIsNotNone(provider.client)
    
    def test_parse_release_date_iso(self):
        """Парсинг даты в формате ISO 8601"""
        from apps.catalog.services.yandex_music import YandexMusicProvider
        from datetime import date
        
        provider = YandexMusicProvider()
        
        result = provider._parse_release_date('2020-12-01T00:00:00+03:00')
        self.assertEqual(result, date(2020, 12, 1))
    
    def test_parse_release_date_simple(self):
        """Парсинг даты в формате YYYY-MM-DD"""
        from apps.catalog.services.yandex_music import YandexMusicProvider
        from datetime import date
        
        provider = YandexMusicProvider()
        
        result = provider._parse_release_date('2020-12-01')
        self.assertEqual(result, date(2020, 12, 1))
    
    def test_parse_release_date_none(self):
        """Парсинг None значения"""
        from apps.catalog.services.yandex_music import YandexMusicProvider
        
        provider = YandexMusicProvider()
        result = provider._parse_release_date(None)
        self.assertIsNone(result)
    
    def test_determine_release_type_single(self):
        """Определение типа релиза - сингл"""
        from apps.catalog.services.yandex_music import YandexMusicProvider
        
        provider = YandexMusicProvider()
        
        class MockAlbum:
            meta_type = 'single'
            track_count = 1
        
        result = provider._determine_release_type(MockAlbum())
        self.assertEqual(result, 'single')
    
    def test_determine_release_type_ep(self):
        """Определение типа релиза - EP"""
        from apps.catalog.services.yandex_music import YandexMusicProvider
        
        provider = YandexMusicProvider()
        
        class MockAlbum:
            meta_type = 'ep'
            track_count = 5
        
        result = provider._determine_release_type(MockAlbum())
        self.assertEqual(result, 'ep')
    
    def test_determine_release_type_album(self):
        """Определение типа релиза - альбом"""
        from apps.catalog.services.yandex_music import YandexMusicProvider
        
        provider = YandexMusicProvider()
        
        class MockAlbum:
            meta_type = None
            track_count = 12
        
        result = provider._determine_release_type(MockAlbum())
        self.assertEqual(result, 'album')
