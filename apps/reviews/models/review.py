from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.contrib.auth import get_user_model
from apps.catalog.models import Release

User = get_user_model()


class Review(models.Model):
    """
    Модель рецензии на релиз.
    
    Оценка производится по 5 критериям:
    - Рифмы (1-10)
    - Структура (1-10)
    - Стиль (1-10)
    - Харизма (1-10)
    - Атмосфера (1-5)
    
    Максимальный балл: 45
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )
    release = models.ForeignKey(
        Release,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Релиз'
    )

    # Criteria (1-10)
    rhymes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Рифмы'
    )
    structure = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Структура'
    )
    style = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Стиль'
    )
    charisma = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Харизма'
    )

    # Atmosphere (1-5)
    atmosphere = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Атмосфера'
    )

    text = models.TextField(
        validators=[MinLengthValidator(100)],
        verbose_name='Текст рецензии'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    total_score = models.PositiveSmallIntegerField(
        editable=False,
        verbose_name='Итоговый балл'
    )

    class Meta:
        verbose_name = 'Рецензия'
        verbose_name_plural = 'Рецензии'
        ordering = ['-created_at']
        unique_together = ['user', 'release']

    def __str__(self):
        return f"{self.user.username} - {self.release} ({self.total_score})"

    def save(self, *args, **kwargs):
        # Calculate total score: (Rhymes + Structure + Style + Charisma) + Atmosphere
        # Max score: 45
        self.total_score = (
            self.rhymes +
            self.structure +
            self.style +
            self.charisma
        ) + self.atmosphere
        super().save(*args, **kwargs)

    def get_criteria_dict(self):
        """Return criteria as dict for radar chart"""
        return {
            'rhymes': self.rhymes,
            'structure': self.structure,
            'style': self.style,
            'charisma': self.charisma,
            'atmosphere': self.atmosphere,
        }
