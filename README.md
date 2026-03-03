# MusicRate

Платформа для рецензирования музыки. Аналог RisaZaTvorchestvo (risazatvorchestvo.com).

## Функционал

- 🔍 Поиск и импорт релизов из Яндекс.Музыки
- ⭐ Оценка релизов по 5 критериям (Рифмы, Структура, Стиль, Харизма, Атмосфера)
- 📊 Радарная диаграмма средних оценок
- 👤 Профили пользователей с системой очков репутации
- 🎨 Тёмная тема с акцентным жёлтым цветом

## Технологический стек

- **Backend:** Python 3.12, Django 5.0+
- **Database:** PostgreSQL
- **Task Queue:** Celery + Redis
- **Frontend:** Tailwind CSS, HTMX, Alpine.js, Chart.js
- **API:** yandex-music-python (неофициальный клиент)

## Быстрый старт

### 1. Клонирование и настройка окружения

```bash
cd musicrate
cp .env.example .env
# Отредактируйте .env файл
```

### 2. Запуск через Docker Compose

```bash
docker-compose up -d
```

### 3. Создание суперпользователя

```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Доступ к приложению

- Приложение: http://localhost:8000
- Админка: http://localhost:8000/admin

## Формула расчёта

```
Total = (Rhymes + Structure + Style + Charisma) + Atmosphere
```

Максимальный балл: **45**

## Структура проекта

```
musicrate/
├── apps/
│   ├── users/          # Пользователи
│   ├── catalog/        # Каталог (Artist, Release)
│   └── reviews/        # Рецензии
├── musicrate/          # Настройки Django
├── templates/          # HTML шаблоны
├── static/            # Статические файлы
├── media/             # Загруженные файлы
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## API Endpoints

| URL | Описание |
|-----|----------|
| `/` | Главная страница с лентой релизов |
| `/release/<slug>/` | Страница релиза |
| `/release/<slug>/review/` | Добавление рецензии |
| `/search/external/` | Поиск по Яндекс.Музыке |
| `/profile/<username>/` | Профиль пользователя |

## Переменные окружения

```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=musicrate
DB_USER=musicrate
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
YANDEX_MUSIC_TOKEN=optional-token
```

## Лицензия

MIT
