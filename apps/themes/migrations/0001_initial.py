# Generated migration for themes app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название темы')),
                ('slug', models.SlugField(unique=True, verbose_name='Слаг')),
                ('theme_type', models.CharField(choices=[('dark', 'Тёмная'), ('light', 'Светлая')], default='dark', max_length=10, verbose_name='Тип темы')),
                ('bg_primary', models.CharField(default='#0a0a0a', max_length=20, verbose_name='Основной фон')),
                ('bg_secondary', models.CharField(default='#141414', max_length=20, verbose_name='Вторичный фон')),
                ('bg_tertiary', models.CharField(default='#1a1a1a', max_length=20, verbose_name='Третичный фон')),
                ('bg_card', models.CharField(default='#2a2a2a', max_length=20, verbose_name='Фон карточек')),
                ('text_primary', models.CharField(default='#ffffff', max_length=20, verbose_name='Основной текст')),
                ('text_secondary', models.CharField(default='#9ca3af', max_length=20, verbose_name='Вторичный текст')),
                ('text_muted', models.CharField(default='#6b7280', max_length=20, verbose_name='Приглушенный текст')),
                ('accent_primary', models.CharField(default='#ffcc00', max_length=20, verbose_name='Основной акцент')),
                ('accent_hover', models.CharField(default='#e6b800', max_length=20, verbose_name='Акцент при наведении')),
                ('border_color', models.CharField(default='#3f3f3f', max_length=20, verbose_name='Цвет границ')),
                ('is_default', models.BooleanField(default=False, verbose_name='Тема по умолчанию')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Тема',
                'verbose_name_plural': 'Темы',
                'ordering': ['is_default', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ThemePreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='users', to='themes.theme', verbose_name='Тема')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='theme_preference', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Предпочтение темы',
                'verbose_name_plural': 'Предпочтения тем',
            },
        ),
    ]
