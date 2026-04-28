#!/usr/bin/env python
"""
Эмуляция Render окружения для тестирования settings.py
"""
import os
import sys

# Устанавливаем Render переменные окружения
os.environ['RENDER'] = 'true'
os.environ['PYTHON_VERSION'] = '3.12.0'

# Если SECRET_KEY не установлен, Render его сгенерирует
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'test-secret-key-for-render-' + 'a' * 50

# DATABASE_URL и REDIS_URL будут установлены Render автоматически
# Здесь используем фиктивные для тестирования
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'postgresql://musicrate:musicrate@localhost:5432/musicrate'

if 'REDIS_URL' not in os.environ:
    os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

# Теперь импортируем Django settings
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicrate.settings')
django.setup()

from django.conf import settings

print("=" * 70)
print("🌐 ЭМУЛЯЦИЯ RENDER ОКРУЖЕНИЯ")
print("=" * 70)

checks = [
    ("RENDER переменная", os.environ.get('RENDER')),
    ("IS_RENDER (в settings)", getattr(settings, 'IS_RENDER', 'NOT SET')),
    ("DEBUG", settings.DEBUG),
    ("ALLOWED_HOSTS", settings.ALLOWED_HOSTS),
    ("CSRF_TRUSTED_ORIGINS", settings.CSRF_TRUSTED_ORIGINS),
    ("SECURE_SSL_REDIRECT", getattr(settings, 'SECURE_SSL_REDIRECT', 'NOT SET')),
    ("SESSION_COOKIE_SECURE", getattr(settings, 'SESSION_COOKIE_SECURE', 'NOT SET')),
    ("CSRF_COOKIE_SECURE", getattr(settings, 'CSRF_COOKIE_SECURE', 'NOT SET')),
    ("SECURE_PROXY_HEADER", getattr(settings, 'SECURE_PROXY_HEADER', 'NOT SET')),
]

print("\n📋 НАСТРОЙКИ НА RENDER:\n")
for key, value in checks:
    if isinstance(value, str) and len(value) > 50:
        value = value[:47] + "..."
    print(f"  {key:<30} = {value}")

print("\n✅ ПРОВЕРКИ УСПЕШНОСТИ:\n")
success = True

if not settings.DEBUG:
    print("  ✅ DEBUG=False (production режим)")
else:
    print("  ❌ DEBUG=True (должен быть False на Render)")
    success = False

if '*.onrender.com' in settings.ALLOWED_HOSTS:
    print("  ✅ ALLOWED_HOSTS содержит *.onrender.com")
else:
    print(f"  ❌ ALLOWED_HOSTS неправильный: {settings.ALLOWED_HOSTS}")
    success = False

if 'https://*.onrender.com' in settings.CSRF_TRUSTED_ORIGINS:
    print("  ✅ CSRF_TRUSTED_ORIGINS содержит https://*.onrender.com")
else:
    print(f"  ❌ CSRF_TRUSTED_ORIGINS неправильный: {settings.CSRF_TRUSTED_ORIGINS}")
    success = False

if settings.SECURE_SSL_REDIRECT:
    print("  ✅ SECURE_SSL_REDIRECT=True")
else:
    print("  ❌ SECURE_SSL_REDIRECT=False (должен быть True)")
    success = False

if settings.SESSION_COOKIE_SECURE:
    print("  ✅ SESSION_COOKIE_SECURE=True")
else:
    print("  ❌ SESSION_COOKIE_SECURE=False")
    success = False

if settings.CSRF_COOKIE_SECURE:
    print("  ✅ CSRF_COOKIE_SECURE=True")
else:
    print("  ❌ CSRF_COOKIE_SECURE=False")
    success = False

if settings.SECURE_PROXY_HEADER == ('HTTP_X_FORWARDED_PROTO', 'https'):
    print("  ✅ SECURE_PROXY_HEADER правильно установлен")
else:
    print(f"  ⚠️  SECURE_PROXY_HEADER: {settings.SECURE_PROXY_HEADER}")

print("\n" + "=" * 70)
if success:
    print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! На Render все будет работать!")
else:
    print("⚠️  ЕСТЬ ПРОБЛЕМЫ - смотри выше")
print("=" * 70 + "\n")
