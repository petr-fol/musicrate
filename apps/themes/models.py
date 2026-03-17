from django.db import models
from django.conf import settings


class Theme(models.Model):
    """Модель темы оформления"""

    THEME_TYPE_CHOICES = [
        ('dark', 'Тёмная'),
        ('light', 'Светлая'),
    ]

    name = models.CharField(max_length=50, verbose_name='Название темы')
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    theme_type = models.CharField(
        max_length=10,
        choices=THEME_TYPE_CHOICES,
        default='dark',
        verbose_name='Тип темы'
    )
    # Цветовые переменные
    bg_primary = models.CharField(max_length=20, default='#0a0a0a', verbose_name='Основной фон')
    bg_secondary = models.CharField(max_length=20, default='#141414', verbose_name='Вторичный фон')
    bg_tertiary = models.CharField(max_length=20, default='#1a1a1a', verbose_name='Третичный фон')
    bg_card = models.CharField(max_length=20, default='#2a2a2a', verbose_name='Фон карточек')
    text_primary = models.CharField(max_length=20, default='#ffffff', verbose_name='Основной текст')
    text_secondary = models.CharField(max_length=20, default='#9ca3af', verbose_name='Вторичный текст')
    text_muted = models.CharField(max_length=20, default='#6b7280', verbose_name='Приглушенный текст')
    accent_primary = models.CharField(max_length=20, default='#ffcc00', verbose_name='Основной акцент')
    accent_hover = models.CharField(max_length=20, default='#e6b800', verbose_name='Акцент при наведении')
    border_color = models.CharField(max_length=20, default='#3f3f3f', verbose_name='Цвет границ')
    is_default = models.BooleanField(default=False, verbose_name='Тема по умолчанию')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
        ordering = ['is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_theme_type_display()})"

    def save(self, *args, **kwargs):
        # Если тема установлена как default, снимаем флаг с других
        if self.is_default:
            Theme.objects.exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    def get_css_variables(self):
        """Возвращает CSS переменные темы"""
        return {
            '--bg-primary': self.bg_primary,
            '--bg-secondary': self.bg_secondary,
            '--bg-tertiary': self.bg_tertiary,
            '--bg-card': self.bg_card,
            '--text-primary': self.text_primary,
            '--text-secondary': self.text_secondary,
            '--text-muted': self.text_muted,
            '--accent-primary': self.accent_primary,
            '--accent-hover': self.accent_hover,
            '--border-color': self.border_color,
        }


class ThemePreference(models.Model):
    """Предпочтения пользователя по темам"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='theme_preference',
        verbose_name='Пользователь'
    )
    theme = models.ForeignKey(
        Theme,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        related_name='users',
        verbose_name='Тема'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Предпочтение темы'
        verbose_name_plural = 'Предпочтения тем'

    def __str__(self):
        return f"{self.user.username} - {self.theme.name if self.theme else 'Нет темы'}"
