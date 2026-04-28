import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Определяем окружение
IS_RENDER = os.getenv('RENDER') == 'true'

# SECRET_KEY - используем переменную окружения или генерируем для разработки
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-this-should-be-changed-in-production-12345678901234567890')

# DEBUG режим
if IS_RENDER:
    DEBUG = False
else:
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# ALLOWED_HOSTS - автоматически для Render
if IS_RENDER:
    ALLOWED_HOSTS = ['*.onrender.com']
else:
    allowed_hosts_env = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1') or 'localhost,127.0.0.1'
    allowed_hosts_env = allowed_hosts_env.strip()
    if allowed_hosts_env == '*' or allowed_hosts_env == '':
        ALLOWED_HOSTS = ['*']
    else:
        ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'django_htmx',
]

LOCAL_APPS = [
    'apps.users',
    'apps.catalog',
    'apps.reviews',
    'apps.themes',
    'apps.i18n',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'musicrate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'apps.themes.context_processors.theme_context',
                'apps.i18n.context_processors.language_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'musicrate.wsgi.application'

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=False)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'musicrate'),
            'USER': os.getenv('DB_USER', 'musicrate'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'musicrate'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Languages
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
    ('kk', 'Қазақша'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Login redirect
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/admin/login/'

# Celery Configuration
REDIS_URL = os.getenv('REDIS_URL', '')
if REDIS_URL:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
else:
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Yandex Music
YANDEX_MUSIC_TOKEN = os.getenv('YANDEX_MUSIC_TOKEN', '')

# Security and Production Settings for Render
CSRF_TRUSTED_ORIGINS = []

# Автоматическая конфигурация CSRF для Render
if IS_RENDER:
    # На Render - хардкодим Render домены
    CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']
else:
    # Локально - добавляем localhost
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]

# Если явно указаны в переменной окружения - добавляем
extra_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if extra_origins:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in extra_origins.split(',') if o.strip()])

# Production-only security settings (включены на Render)
if IS_RENDER or not DEBUG:
    # HTTPS/SSL Configuration
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'"),
        'style-src': ("'self'", "'unsafe-inline'"),
        'img-src': ("'self'", 'data:', 'https:'),
        'font-src': ("'self'",),
    }
    
    # HSTS Configuration
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Proxy Headers (важно для Render)
    SECURE_PROXY_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
