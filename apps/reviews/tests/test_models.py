"""
Тесты для модели Review
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from apps.reviews.models import Review
from apps.catalog.models import Artist, Release
from apps.tests.base import BaseTestCase

User = get_user_model()


class ReviewModelTest(BaseTestCase):
    """Тесты для модели Review"""
    
    def setUp(self):
        super().setUp()
        self.artist = Artist.objects.create(name='Test Artist')
        self.release = Release.objects.create(
            title='Test Album',
            artist=self.artist,
            release_type='album'
        )
    
    def test_review_creation(self):
        """Создание рецензии"""
        review = Review.objects.create(
            user=self.user,
            release=self.release,
            rhymes=8,
            structure=7,
            style=9,
            charisma=8,
            atmosphere=4,
            text='This is a test review. ' * 10
        )
        
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.release, self.release)
        self.assertEqual(review.total_score, 36)
    
    def test_review_total_score_calculation(self):
        """Расчёт итогового балла"""
        review = Review.objects.create(
            user=self.user,
            release=self.release,
            rhymes=10,
            structure=10,
            style=10,
            charisma=10,
            atmosphere=5,
            text='Maximum score review. ' * 10
        )
        
        self.assertEqual(review.total_score, 45)
    
    def test_review_minimum_score(self):
        """Минимальный балл"""
        review = Review.objects.create(
            user=self.user,
            release=self.release,
            rhymes=1,
            structure=1,
            style=1,
            charisma=1,
            atmosphere=1,
            text='Minimum score review. ' * 10
        )
        
        self.assertEqual(review.total_score, 5)
    
    def test_review_criteria_validation(self):
        """Валидация критериев (1-10)"""
        from django.core.exceptions import ValidationError
        
        review = Review(
            user=self.user,
            release=self.release,
            rhymes=11,  # Больше максимума
            structure=5,
            style=5,
            charisma=5,
            atmosphere=3,
            text='Invalid review. ' * 10
        )
        
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_review_atmosphere_validation(self):
        """Валидация атмосферы (1-5)"""
        from django.core.exceptions import ValidationError
        
        review = Review(
            user=self.user,
            release=self.release,
            rhymes=5,
            structure=5,
            style=5,
            charisma=5,
            atmosphere=6,  # Больше максимума
            text='Invalid atmosphere. ' * 10
        )
        
        with self.assertRaises(ValidationError):
            review.full_clean()
    
    def test_review_text_min_length(self):
        """Минимальная длина текста"""
        with self.assertRaises(ValidationError):
            review = Review(
                user=self.user,
                release=self.release,
                rhymes=5,
                structure=5,
                style=5,
                charisma=5,
                atmosphere=3,
                text='Short'  # Меньше 100 символов
            )
            review.full_clean()
    
    def test_review_unique_user_release(self):
        """Уникальность рецензии на релиз"""
        Review.objects.create(
            user=self.user,
            release=self.release,
            rhymes=5,
            structure=5,
            style=5,
            charisma=5,
            atmosphere=3,
            text='First review. ' * 10
        )
        
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                user=self.user,
                release=self.release,
                rhymes=8,
                structure=8,
                style=8,
                charisma=8,
                atmosphere=4,
                text='Duplicate review. ' * 10
            )
    
    def test_review_get_criteria_dict(self):
        """Получение словаря критериев"""
        review = Review.objects.create(
            user=self.user,
            release=self.release,
            rhymes=8,
            structure=7,
            style=9,
            charisma=8,
            atmosphere=4,
            text='Test review. ' * 10
        )
        
        criteria = review.get_criteria_dict()
        
        self.assertEqual(criteria['rhymes'], 8)
        self.assertEqual(criteria['structure'], 7)
        self.assertEqual(criteria['style'], 9)
        self.assertEqual(criteria['charisma'], 8)
        self.assertEqual(criteria['atmosphere'], 4)
    
    def test_review_str_representation(self):
        """Строковое представление"""
        review = Review.objects.create(
            user=self.user,
            release=self.release,
            rhymes=8,
            structure=7,
            style=9,
            charisma=8,
            atmosphere=4,
            text='Test review. ' * 10
        )
        
        self.assertEqual(str(review), 'testuser - Test Artist - Test Album (36)')
    
    def test_review_ordering(self):
        """Сортировка рецензий (новые сначала)"""
        review1 = Review.objects.create(
            user=self.user,
            release=self.release,
            rhymes=5, structure=5, style=5, charisma=5, atmosphere=3,
            text='Old review. ' * 10
        )
        review2 = Review.objects.create(
            user=self.superuser,
            release=self.release,
            rhymes=8, structure=8, style=8, charisma=8, atmosphere=4,
            text='New review. ' * 10
        )
        
        reviews = list(Review.objects.all())
        self.assertEqual(reviews[0], review2)
