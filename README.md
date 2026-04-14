# MusicRate

Платформа для рецензирования музыки. Аналог RisaZaTvorchestvo (risazatvorchestvo.com).

## Функционал

- 🔍 Поиск и импорт релизов из Яндекс.Музыки
- ⭐ Оценка релизов по 5 критериям (Рифмы, Структура, Стиль, Харизма, Атмосфера)
- 📊 Радарная диаграмма средних оценок
- 👤 Профили пользователей с системой очков репутации
- 🎨 Тёмная тема с акцентным жёлтым цветом
- 🌍 Многоязычность (Русский, English, Қазақша)
- 🎨 Кастомные темы оформления (6 тем)

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

## Деплой на Render (бесплатно)

### Автоматический деплой через render.yaml

1. **Залейте проект на GitHub** (если ещё не залит):
   ```bash
   git add .
   git commit -m "Add Render deployment config"
   git push origin main
   ```

2. **Перейдите на [render.com](https://render.com)**:
   - Зарегистрируйтесь/войдите через GitHub
   - Нажмите **"New +"** → **"Blueprint"**
   - Выберите репозиторий `musicrate`
   - Нажмите **"Apply"**

3. **Готово!** Render автоматически создаст:
   - Веб-сервис (Django + Gunicorn)
   - PostgreSQL базу данных
   - Redis для Celery

4. **Создайте суперпользователя**:
   - Перейдите в Dashboard → ваш сервис → **"Shell"**
   - Выполните: `python manage.py createsuperuser`

5. **Доступ к приложению**:
   - URL вида: `https://musicrate.onrender.com`
   - Админка: `https://musicrate.onrender.com/admin`

### Примечания

- Бесплатный тариф: сервис "засыпает" после 15 минут неактивности
- Первый запрос после "сна" занимает ~30 секунд
- Для постоянного доступа используйте платный тариф ($7/мес)

---

## Деплой на Railway

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
│   ├── reviews/        # Рецензии
│   ├── themes/         # Темы оформления
│   └── i18n/           # Интернационализация
├── locale/             # Файлы переводов
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
| `/themes/set/` | Переключение темы |
| `/i18n/set/` | Переключение языка |

## Языки

Приложение поддерживает 3 языка:

- **Русский** (ru) — по умолчанию
- **English** (en)
- **Қазақша** (kk)

Переключение языка доступно в шапке сайта для авторизованных пользователей.

## Темы оформления

Доступно 6 тем оформления:

- **Тёмная классика** — черно-оранжевая (по умолчанию)
- **Светлая классика** — бело-оранжевая
- **Ночной океан** — сине-голубая
- **Матрица** — черно-зелёная
- **Минимализм** — чёрно-белая
- **Киберпанк** — фиолетово-тёмная

Переключение тем доступно в шапке сайта для авторизованных пользователей.

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

## Тесты

```bash
# Запуск всех тестов
docker-compose exec web python manage.py test apps

# Запуск тестов с покрытием
docker-compose exec web python manage.py test apps --verbosity=2
```

## Лицензия

MIT
