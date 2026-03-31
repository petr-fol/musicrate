# MusicRate — Техническая документация

Платформа для рецензирования музыки с интеграцией Яндекс.Музыки.

---

## 📋 Оглавление

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура](#архитектура)
3. [Модели данных](#модели-данных)
4. [Бизнес-логика](#бизнес-логика)
5. [API и URL-маршруты](#api-и-url-маршруты)
6. [Стек технологий](#стек-технологий)
7. [Настройка окружения](#настройка-окружения)
8. [Docker и развёртывание](#docker-и-развёртывание)
9. [Структура проекта](#структура-проекта)
10. [Ключевые особенности реализации](#ключевые-особенности-реализации)
11. [Расширение функционала](#расширение-функционала)
12. [Новые функции (v2)](#новые-функции-v2)

---

## Обзор проекта

**MusicRate** — веб-приложение для публикации и оценки музыкальных релизов (альбомов, синглов, EP). Пользователи могут импортировать релизы из Яндекс.Музыки, писать рецензии и оценивать их по 5 критериям.

**Аналог:** RisaZaTvorchestvo (risazatvorchestvo.com)

---

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                        │
│  (Tailwind CSS + HTMX + Alpine.js + Chart.js)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Catalog   │  │   Reviews   │  │    Users    │          │
│  │    (app)    │  │    (app)    │  │    (app)    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Yandex Music Service                     │   │
│  │         (неофициальный API клиент)                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │  Redis (Celery) │
│   (Database)    │    │  (Task Queue)   │
└─────────────────┘    └─────────────────┘
```

### Компоненты

| Компонент | Описание |
|-----------|----------|
| **web** | Django-сервер (Gunicorn в production) |
| **db** | PostgreSQL 16 (хранение данных) |
| **redis** | Redis 7 (брокер для Celery) |
| **celery** | Worker для фоновых задач |
| **celery-beat** | Планировщик периодических задач |

---

## Модели данных

### apps/users/models.py — User

```python
User(AbstractUser)
├── avatar: ImageField (avatars/)
├── bio: TextField
└── points: PositiveIntegerField (репутация, по умолчанию 0)
```

**Методы:**
- `get_display_name()` — возвращает ФИО или username

---

### apps/catalog/models.py — Artist, Release

```python
Artist
├── name: CharField(255)
├── slug: SlugField (уникальный, автогенерация)
├── yandex_id: CharField(100, blank)
└── image: ImageField (artists/, nullable)
```

```python
Release
├── title: CharField(255)
├── slug: SlugField (уникальный, автогенерация)
├── artist: ForeignKey → Artist
├── release_type: Choices ('single', 'ep', 'album')
├── cover: ImageField (releases/, nullable)
├── release_date: DateField (nullable)
├── yandex_id: CharField(100, unique, nullable)
├── average_score: DecimalField (4,2, default=0)
└── created_at: DateTimeField (auto)
```

**Методы Release:**
- `update_average_score()` — пересчитывает средний балл релиза
- `get_absolute_url()` — URL страницы релиза

---

### apps/reviews/models.py — Review

```python
Review
├── user: ForeignKey → User
├── release: ForeignKey → Release
├── rhymes: PositiveSmallIntegerField (1-10)
├── structure: PositiveSmallIntegerField (1-10)
├── style: PositiveSmallIntegerField (1-10)
├── charisma: PositiveSmallIntegerField (1-10)
├── atmosphere: PositiveSmallIntegerField (1-5)
├── text: TextField (min 100 символов)
├── created_at: DateTimeField (auto)
└── total_score: PositiveSmallIntegerField (вычисляемое)
```

**Ограничения:**
- `unique_together = ['user', 'release']` — одна рецензия на релиз

**Методы:**
- `get_criteria_dict()` — возвращает словарь критериев для Chart.js

---

## Бизнес-логика

### Формула расчёта баллов

```
Total = (Rhymes + Structure + Style + Charisma) + Atmosphere
```

| Критерий | Диапазон | Вес |
|----------|----------|-----|
| Рифмы | 1-10 | 1x |
| Структура | 1-10 | 1x |
| Стиль | 1-10 | 1x |
| Харизма | 1-10 | 1x |
| Атмосфера | 1-5 | 1x |

**Максимальный балл:** 45 (40 + 5)

### Система репутации

| Действие | Изменение очков |
|----------|-----------------|
| Создание рецензии | +10 |
| Удаление рецензии | -10 (не ниже 0) |

Реализовано через сигналы Django (`apps/reviews/signals.py`):
- `post_save` — начисление при создании
- `post_delete` — списание при удалении

---

## API и URL-маршруты

### apps/catalog/urls.py

| URL | View | Описание |
|-----|------|----------|
| `/` | `index_view` | Главная страница (лента релизов) |
| `/release/<slug>/` | `release_detail_view` | Страница релиза + рецензии |
| `/search/external/` | `api_search_view` | Поиск в Яндекс.Музыке (HTMX) |
| `/import/release/<yandex_id>/` | `import_release_view` | Импорт релиза (POST, login_required) |

### apps/reviews/urls.py

| URL | View | Описание |
|-----|------|----------|
| `/release/<slug>/review/` | `add_review_view` | Форма добавления рецензии (login_required) |

### apps/users/urls.py

| URL | View | Описание |
|-----|------|----------|
| `/profile/<username>/` | `profile_view` | Профиль пользователя + список рецензий |

---

## Стек технологий

### Backend

| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.12 | Язык программирования |
| Django | 5.0.x | Веб-фреймворк |
| PostgreSQL | 16 | Основная БД |
| Redis | 7 | Брокер для Celery |
| Celery | 5.3.4 | Очереди задач |
| yandex-music | 2.1.x | Клиент Яндекс.Музыки |
| Pillow | 10.1.x | Работа с изображениями |
| cyrtranslit | 1.0.x | Транслитерация кириллицы |

### Frontend

| Технология | Назначение |
|------------|------------|
| Tailwind CSS | Стилизация (CDN) |
| HTMX | Динамические запросы (AJAX без JS) |
| Alpine.js | Реактивность (CDN) |
| Chart.js | Радарные диаграммы оценок |

### Deployment

| Технология | Назначение |
|------------|------------|
| Docker | Контейнеризация |
| Gunicorn | WSGI-сервер (production) |
| WhiteNoise | Раздача статики |
| Railway | Хостинг |

---

## Настройка окружения

### Переменные окружения (.env)

```env
# Отладка
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# База данных
DB_NAME=musicrate
DB_USER=musicrate
DB_PASSWORD=musicrate_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Яндекс.Музыка (опционально)
YANDEX_MUSIC_TOKEN=

# Production-дополнения
ALLOWED_HOSTS=*
DATABASE_URL=postgresql://...  # для Railway
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## Docker и развёртывание

### Локальный запуск

```bash
# Клонирование и настройка
git clone <repo>
cd musicrate
cp .env.example .env

# Запуск всех сервисов
docker-compose up -d

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Просмотр логов
docker-compose logs -f
```

### Make-команды

| Команда | Описание |
|---------|----------|
| `make up` | Запуск контейнеров |
| `make down` | Остановка контейнеров |
| `make migrate` | Применение миграций |
| `make migrations` | Создание миграций |
| `make shell` | Django shell |
| `make superuser` | Создание админа |
| `make test` | Запуск тестов |
| `make db-reset` | Сброс БД и миграции |
| `make setup` | Полный цикл настройки |

### Production (Railway)

1. Подключить GitHub-репозиторий в Railway
2. Добавить PostgreSQL и Redis
3. Установить переменные окружения
4. Автоматический деплой при push в main

**railway.toml:**
```toml
[deploy]
startCommand = "python manage.py migrate && gunicorn musicrate.wsgi:application --bind 0.0.0.0:$PORT"
healthcheckPath = "/"
healthcheckTimeout = 100
```

---

## Структура проекта

```
musicrate/
├── .env.example              # Шаблон переменных окружения
├── .env.railway.example      # Шаблон для Railway
├── docker-compose.yml        # Docker-оркестрация
├── Dockerfile                # Сборка образа
├── Makefile                  # Make-команды
├── manage.py                 # Django CLI
├── requirements.txt          # Python-зависимости
├── railway.toml              # Конфиг Railway
├── Procfile                  # Procfile для Railway
├── DEPLOY.md                 # Гайд по деплою
├── README.md                 # Краткая документация
│
├── musicrate/                # Настройки Django
│   ├── __init__.py
│   ├── celery.py             # Celery-конфигурация
│   ├── settings.py           # Настройки проекта
│   ├── urls.py               # Корневые URL
│   └── wsgi.py               # WSGI-точка входа
│
├── apps/                     # Django-приложения
│   ├── __init__.py
│   │
│   ├── catalog/              # Каталог релизов
│   │   ├── models.py         # Artist, Release
│   │   ├── views.py          # Views: index, detail, search, import
│   │   ├── services.py       # YandexMusicProvider (API клиент)
│   │   ├── urls.py           # URL-маршруты
│   │   ├── admin.py          # Admin-регистрация
│   │   └── migrations/
│   │
│   ├── reviews/              # Рецензии
│   │   ├── models.py         # Review
│   │   ├── views.py          # Views: add_review
│   │   ├── forms.py          # ReviewForm
│   │   ├── signals.py        # Сигналы репутации
│   │   ├── urls.py           # URL-маршруты
│   │   ├── admin.py          # Admin-регистрация
│   │   └── migrations/
│   │
│   └── users/                # Пользователи
│       ├── models.py         # Custom User
│       ├── views.py          # Views: profile
│       ├── urls.py           # URL-маршруты
│       ├── admin.py          # Admin-регистрация
│       └── migrations/
│
├── templates/                # HTML-шаблоны
│   ├── base.html             # Базовый шаблон
│   ├── catalog/
│   │   ├── index.html        # Главная страница
│   │   ├── release_detail.html
│   │   ├── search.html
│   │   └── partials/
│   ├── reviews/
│   │   └── add_review.html
│   └── users/
│       └── profile.html
│
├── static/                   # Статические файлы
│   └── css/
│       └── custom.css
│
└── media/                    # Загруженные файлы
    ├── artists/
    ├── releases/
    └── avatars/
```

---

## Ключевые особенности реализации

### 1. Генерация slug для кириллицы

**Файл:** `apps/catalog/models.py`

```python
def cyrillic_slugify(value):
    """Транслитерация кириллицы → латиница + slugify"""
    if value:
        return slugify(cyrtranslit.to_latin(value, 'ru'))
    return None
```

**Пример:** «Кино» → `kino`, «Мой район» → `moj-rajon`

---

### 2. Импорт из Яндекс.Музыки

**Файл:** `apps/catalog/services.py`

Класс `YandexMusicProvider`:
- `search(query, limit=10)` — поиск релизов
- `import_release(yandex_id)` — импорт с загрузкой обложки и изображения артиста
- `_download_image(instance, url, field_name)` — скачивание и сохранение изображений

**Определение типа релиза:**
```python
if track_count <= 3:    → single
elif track_count <= 6:  → ep
else:                   → album
```

---

### 3. Радарная диаграмма оценок

**Файл:** `templates/catalog/release_detail.html`

Chart.js визуализирует средние значения по 5 критериям:
```javascript
new Chart(ctx, {
    type: 'radar',
    data: {
        labels: ['Рифмы', 'Структура', 'Стиль', 'Харизма', 'Атмосфера'],
        datasets: [{
            label: 'Средние оценки',
            data: [avg_rhymes, avg_structure, avg_style, avg_charisma, avg_atmosphere]
        }]
    }
});
```

---

### 4. HTMX для динамического поиска

**Файл:** `templates/catalog/partials/search_results.html`

Поиск работает без перезагрузки страницы:
```html
<input name="q" 
       hx-get="/search/external/" 
       hx-trigger="keyup changed delay:300ms"
       hx-target="#search-results">
```

---

### 5. Сигналы для репутации

**Файл:** `apps/reviews/signals.py`

```python
@receiver(post_save, sender=Review)
def update_release_average_score_on_save(sender, instance, created, **kwargs):
    instance.release.update_average_score()
    if created:
        instance.user.points += 10
        instance.user.save()
```

---

### 6. Кастомная модель пользователя

**Файл:** `apps/users/models.py`

```python
AUTH_USER_MODEL = 'users.User'
```

Расширяет `AbstractUser` полями: `avatar`, `bio`, `points`

---

### 7. Настройка статики и медиа

**Файл:** `musicrate/settings.py`

```python
# Static files (WhiteNoise для production)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## Расширение функционала

### Добавление нового поля в модель

1. Изменить модель в `apps/<app>/models.py`
2. Создать миграцию: `make migrations`
3. Применить: `make migrate`

### Добавление нового view

1. Создать функцию в `apps/<app>/views.py`
2. Добавить URL в `apps/<app>/urls.py`
3. Создать шаблон в `templates/<app>/`

### Фоновые задачи (Celery)

```python
# apps/catalog/tasks.py
from celery import shared_task

@shared_task
def import_release_task(yandex_id):
    provider = YandexMusicProvider()
    return provider.import_release(yandex_id)
```

---

## Полезные команды

```bash
# Django shell
docker-compose exec web python manage.py shell

# Создать миграции
docker-compose exec web python manage.py makemigrations

# Применить миграции
docker-compose exec web python manage.py migrate

# Собрать статику
docker-compose exec web python manage.py collectstatic --noinput

# Тесты
docker-compose exec web python manage.py test

# Суперпользователь
docker-compose exec web python manage.py createsuperuser
```

---

## Новые функции (v2)

### Расширенный поиск

**Файлы:** `apps/catalog/views.py`, `templates/catalog/search.html`, `templates/catalog/partials/search_results.html`

Поиск теперь работает по трём категориям:

| Тип | Описание | Источник |
|-----|----------|----------|
| **Релизы** | Альбомы, синглы, EP на платформе | Локальная БД + Яндекс.Музыка API |
| **Артисты** | Исполнители с релизами на платформе | Локальная БД |
| **Пользователи** | Зарегистрированные пользователи | Локальная БД |

**Реализация:**
- Вкладки для фильтрации результатов (Alpine.js)
- HTMX для динамической подгрузки без перезагрузки
- Отображение результатов в виде карточек

```python
# apps/catalog/views.py
def api_search_view(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')
    
    results = {
        'releases': Release.objects.filter(Q(title__icontains=query) | Q(artist__name__icontains=query))[:20],
        'artists': Artist.objects.filter(Q(name__icontains=query))[:20],
        'users': User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )[:20],
    }
```

---

### Страница артиста

**Файлы:** `apps/catalog/views.py`, `templates/catalog/artist_detail.html`

Страница `/artist/<slug>/` отображает:
- Информацию об артисте (фото, название, статистика)
- Ссылку на Яндекс.Музыку
- Разделы с релизами: Альбомы, EP, Синглы
- Сетку карточек релизов с оценками

```python
# apps/catalog/views.py
def artist_detail_view(request, slug):
    artist = get_object_or_404(Artist, slug=slug)
    releases = artist.releases.select_related('artist').order_by('-release_date', '-created_at')
    
    albums = releases.filter(release_type='album')
    eps = releases.filter(release_type='ep')
    singles = releases.filter(release_type='single')
```

---

### Система рекомендаций

**Файлы:** `apps/catalog/services.py`, `apps/catalog/views.py`, `templates/catalog/index.html`

Алгоритм рекомендаций для авторизованных пользователей:

1. **Анализ предпочтений:**
   - Подсчёт количества оценённых релизов по артистам
   - Выделение топ-3 любимых артистов

2. **Подбор релизов:**
   - Новые релизы от любимых артистов (не оценённые пользователем)
   - Если недостаточно — похожие артисты (через общих слушателей)

3. **Отображение:**
   - Блок "Рекомендуем вам" на главной странице
   - Только для авторизованных пользователей

```python
# apps/catalog/services.py
def get_user_recommendations(user, limit=6):
    user_reviews = Review.objects.filter(user=user).select_related('release__artist')
    
    if not user_reviews.exists():
        return list(Release.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-average_score', '-review_count')[:limit])
    
    # Топ-3 любимых артиста
    top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Релизы, которые пользователь ещё не оценил
    recommended = Release.objects.filter(
        artist_id__in=top_artist_ids
    ).exclude(id__in=reviewed_release_ids)[:limit]
```

---

### Обновлённые URL-маршруты

| URL | View | Описание |
|-----|------|----------|
| `/` | `index_view` | Главная + рекомендации |
| `/artist/<slug>/` | `artist_detail_view` | Страница артиста |
| `/release/<slug>/` | `release_detail_view` | Страница релиза |
| `/search/external/` | `api_search_view` | Расширенный поиск |
| `/import/release/<yandex_id>/` | `import_release_view` | Импорт релиза |
| `/profile/<username>/` | `profile_view` | Профиль пользователя |
| `/themes/set/` | `set_theme` | Переключение темы |
| `/i18n/set/` | `set_language` | Переключение языка |

---

## Новые функции (v3) — Интернационализация и Темы

### Многоязычность (i18n)

**Файлы:** `apps/i18n/`, `locale/`

Приложение поддерживает 3 языка:
- **Русский** (ru) — по умолчанию
- **English** (en)
- **Қазақша** (kk)

**Реализация:**
- Django i18n framework
- Язык сохраняется в cookie и сессии
- Переключатель в шапке сайта (HTMX)
- Файлы переводов в `locale/<lang>/LC_MESSAGES/django.po`

```python
# apps/i18n/views.py
@require_POST
def set_language(request):
    lang_code = request.POST.get('language')
    # Сохранение в сессии и cookie
```

**Переключение языка:**
```bash
# Через форму
POST /i18n/set/
language=en&next=/

# Через HTMX
hx-post="/i18n/set/"
```

### Кастомные темы оформления

**Файлы:** `apps/themes/`, `templates/themes/`

Доступно 6 тем оформления через систему CSS переменных:

| Тема | Тип | Цвета |
|------|-----|-------|
| Тёмная классика | 🌙 Тёмная | Черно-оранжевая (по умолчанию) |
| Светлая классика | ☀️ Светлая | Бело-оранжевая |
| Ночной океан | 🌙 Тёмная | Сине-голубая |
| Матрица | 🌙 Тёмная | Черно-зелёная |
| Минимализм | ☀️ Светлая | Чёрно-белая |
| Киберпанк | 🌙 Тёмная | Фиолетово-тёмная |

**Модель темы:**
```python
class Theme(models.Model):
    name = CharField()
    slug = SlugField(unique=True)
    theme_type = ChoiceField(['dark', 'light'])
    # CSS переменные
    bg_primary = CharField()
    accent_primary = CharField()
    ...
```

**Хранение предпочтений:**
```python
class ThemePreference(models.Model):
    user = OneToOneField(User)
    theme = ForeignKey(Theme)
```

### Обновлённая структура проекта

```
musicrate/
├── apps/
│   ├── catalog/        # Каталог релизов
│   ├── reviews/        # Рецензии
│   ├── users/          # Пользователи
│   ├── themes/         # Темы оформления (+)
│   └── i18n/           # Интернационализация (+)
├── locale/             # Файлы переводов (+)
│   ├── ru/LC_MESSAGES/
│   ├── en/LC_MESSAGES/
│   └── kk/LC_MESSAGES/
├── templates/
│   ├── themes/partials/    # Переключатель тем (+)
│   └── i18n/partials/      # Переключатель языков (+)
└── ...
```

### Технические детали

**Зависимости:**
- Не требует новых пакетов
- Использует: Django i18n, HTMX, Alpine.js, CSS Variables

**Производительность:**
- Ленивая загрузка переводов
- CSS переменные для тем (без перерисовки)
- Кэширование в cookie/sessions

**Расширение:**
- Для добавления языка: создать `.po` файл в `locale/<lang>/`
- Для новой темы: создать запись в админке Theme
- Для перевода: `django-admin makemessages -l <lang>`

---

## Контакты и поддержка

- **GitHub:** [репозиторий проекта]
- **Документация:** README.md, DEPLOY.md
- **Логи:** `docker-compose logs -f`

---

*Документация актуальна для версии на Django 5.0+, Python 3.12*
