from django.db import migrations


def create_default_themes(apps, schema_editor):
    """Создаёт темы по умолчанию"""
    Theme = apps.get_model('themes', 'Theme')

    # Тёмная тема по умолчанию (текущая черно-оранжевая)
    Theme.objects.create(
        name='Тёмная классика',
        slug='dark-classic',
        theme_type='dark',
        is_default=True,
        is_active=True,
        bg_primary='#0a0a0a',
        bg_secondary='#141414',
        bg_tertiary='#1a1a1a',
        bg_card='#2a2a2a',
        text_primary='#ffffff',
        text_secondary='#9ca3af',
        text_muted='#6b7280',
        accent_primary='#ffcc00',
        accent_hover='#e6b800',
        border_color='#3f3f3f',
    )

    # Светлая тема по умолчанию
    Theme.objects.create(
        name='Светлая классика',
        slug='light-classic',
        theme_type='light',
        is_default=False,
        is_active=True,
        bg_primary='#ffffff',
        bg_secondary='#f3f4f6',
        bg_tertiary='#e5e7eb',
        bg_card='#ffffff',
        text_primary='#111827',
        text_secondary='#4b5563',
        text_muted='#9ca3af',
        accent_primary='#f59e0b',
        accent_hover='#d97706',
        border_color='#d1d5db',
    )

    # Тёмная тема (синий акцент)
    Theme.objects.create(
        name='Ночной океан',
        slug='night-ocean',
        theme_type='dark',
        is_default=False,
        is_active=True,
        bg_primary='#0f172a',
        bg_secondary='#1e293b',
        bg_tertiary='#334155',
        bg_card='#1e293b',
        text_primary='#f1f5f9',
        text_secondary='#94a3b8',
        text_muted='#64748b',
        accent_primary='#38bdf8',
        accent_hover='#0ea5e9',
        border_color='#334155',
    )

    # Тёмная тема (зелёный акцент)
    Theme.objects.create(
        name='Матрица',
        slug='matrix',
        theme_type='dark',
        is_default=False,
        is_active=True,
        bg_primary='#0a0a0a',
        bg_secondary='#0f1f0f',
        bg_tertiary='#1a2f1a',
        bg_card='#0f1f0f',
        text_primary='#00ff00',
        text_secondary='#00cc00',
        text_muted='#009900',
        accent_primary='#00ff00',
        accent_hover='#00cc00',
        border_color='#003300',
    )

    # Светлая тема (минимализм)
    Theme.objects.create(
        name='Минимализм',
        slug='minimalism',
        theme_type='light',
        is_default=False,
        is_active=True,
        bg_primary='#fafafa',
        bg_secondary='#ffffff',
        bg_tertiary='#f5f5f5',
        bg_card='#ffffff',
        text_primary='#262626',
        text_secondary='#525252',
        text_muted='#a3a3a3',
        accent_primary='#171717',
        accent_hover='#404040',
        border_color='#e5e5e5',
    )

    # Тёмная тема (фиолетовый акцент)
    Theme.objects.create(
        name='Киберпанк',
        slug='cyberpunk',
        theme_type='dark',
        is_default=False,
        is_active=True,
        bg_primary='#0d0d1a',
        bg_secondary='#1a1a2e',
        bg_tertiary='#16213e',
        bg_card='#1a1a2e',
        text_primary='#eaeaea',
        text_secondary='#b8b8d1',
        text_muted='#6c6c8a',
        accent_primary='#a855f7',
        accent_hover='#9333ea',
        border_color='#2d2d5a',
    )


def delete_default_themes(apps, schema_editor):
    """Удаляет темы по умолчанию"""
    Theme = apps.get_model('themes', 'Theme')
    Theme.objects.filter(slug__in=[
        'dark-classic',
        'light-classic',
        'night-ocean',
        'matrix',
        'minimalism',
        'cyberpunk',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('themes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_themes, delete_default_themes),
    ]
