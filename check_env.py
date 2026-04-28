#!/usr/bin/env python
"""
Проверка переменных окружения Django
Запуск: python check_env.py
"""

import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicrate.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("🔍 ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
print("=" * 60)

checks = [
    ("DEBUG", settings.DEBUG),
    ("ALLOWED_HOSTS", settings.ALLOWED_HOSTS),
    ("CSRF_TRUSTED_ORIGINS", getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET')),
    ("SECURE_SSL_REDIRECT", getattr(settings, 'SECURE_SSL_REDIRECT', 'NOT SET')),
    ("SESSION_COOKIE_SECURE", getattr(settings, 'SESSION_COOKIE_SECURE', 'NOT SET')),
    ("CSRF_COOKIE_SECURE", getattr(settings, 'CSRF_COOKIE_SECURE', 'NOT SET')),
    ("SECURE_PROXY_HEADER", getattr(settings, 'SECURE_PROXY_HEADER', 'NOT SET')),
]

print("\n📋 ОСНОВНЫЕ НАСТРОЙКИ:\n")
for key, value in checks:
    if isinstance(value, str) and len(value) > 50:
        value = value[:47] + "..."
    print(f"  {key:<30} = {value}")

print("\n🗄️  БАЗА ДАННЫХ:\n")
db_config = settings.DATABASES['default']
print(f"  Engine:    {db_config['ENGINE']}")
print(f"  Host:      {db_config.get('HOST', 'default')}")
print(f"  Port:      {db_config.get('PORT', 'default')}")
print(f"  Name:      {db_config.get('NAME', 'unknown')}")

print("\n🔴 REDIS:\n")
redis_url = os.getenv('REDIS_URL', 'NOT SET')
print(f"  REDIS_URL: {redis_url if redis_url != 'NOT SET' else '❌ NOT SET'}")

print("\n🎵 YANDEX MUSIC:\n")
yandex_token = os.getenv('YANDEX_MUSIC_TOKEN', '')
if yandex_token:
    print(f"  Token установлен: ✅ (первые 5: {yandex_token[:5]}...)")
else:
    print(f"  Token: ❌ НЕ УСТАНОВЛЕН (опционально)")

print("\n" + "=" * 60)
if settings.DEBUG:
    print("⚠️  ВНИМАНИЕ: DEBUG=True (для production должен быть False!)")
else:
    print("✅ DEBUG=False (production режим)")
print("=" * 60 + "\n")
