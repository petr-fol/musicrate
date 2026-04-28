# 🚀 Render Deployment Guide

## Быстрый старт

### 1. Залейте проект на GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Подключите Render к GitHub

1. Зайдите на [render.com](https://render.com)
2. Войдите или создайте аккаунт через GitHub
3. Нажмите **"New +"** → **"Web Service"**
4. Выберите **"Deploy an existing GitHub repository"**
5. Найдите репозиторий `musicrate` и нажмите **"Connect"**

### 3. Настройте Web Service

1. **Name**: musicrate (или другое имя)
2. **Runtime**: Python 3
3. **Build Command**: Должна автоматически подхватиться из `render.yaml`
4. **Start Command**: Должна автоматически подхватиться из `render.yaml`
5. **Instance Type**: Выберите Free (для тестирования) или платный тариф

### 4. Добавьте PostgreSQL Database

1. Нажмите **"+"** → **"PostgreSQL"**
2. Заполните:
   - **Name**: musicrate-db
   - **Database**: musicrate
   - **User**: musicrate
   - **Region**: выберите ближайший
3. Нажмите **"Create Database"**

### 5. Добавьте Redis (для Celery)

1. Нажмите **"+"** → **"Redis"**
2. Заполните:
   - **Name**: musicrate-redis
   - **Region**: выберите ближайший
3. Нажмите **"Create Redis"**

### 6. Проверьте переменные окружения

После добавления БД и Redis, Render должен автоматически добавить:
- `DATABASE_URL`
- `REDIS_URL`

Дополнительно убедитесь, что установлены:
- `SECRET_KEY` (сгенерируется автоматически в `render.yaml`)
- `DEBUG=False`
- `ALLOWED_HOSTS=*.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`

Если нужно добавить переменную вручную:
1. Перейдите в **Environment** вашего Web Service
2. Нажмите **"Add Environment Variable"**
3. Заполните **Key** и **Value**

### 7. Деплой

1. Render должен автоматически запустить деплой после подключения
2. Ожидайте ~5-10 минут первый деплой
3. После завершения сайт будет доступен по ссылке вида:
   ```
   https://musicrate-XXXXX.onrender.com
   ```

### 8. Создайте суперпользователя

Откройте Shell в Render:
1. Перейдите в **Web Service** → **Shell**
2. Выполните:
   ```bash
   python manage.py createsuperuser
   ```

---

## Структура файлов конфигурации

- **render.yaml** — основной конфиг для Render
  - Содержит команды build и start
  - Описывает базу данных и Redis
  - Определяет переменные окружения

- **musicrate/settings.py** — Django настройки
  - Security конфигурация для production
  - Поддержка HTTPS и прокси-заголовков
  - CSRF и CORS настройки

- **requirements.txt** — все необходимые пакеты

---

## Решение проблем

### Ошибка 400 (Bad Request)
**Причина**: Неправильная конфигурация ALLOWED_HOSTS или CSRF_TRUSTED_ORIGINS

**Решение**: 
- Проверьте переменные окружения в Render Dashboard
- `ALLOWED_HOSTS` должен содержать ваш домен (*.onrender.com)
- `CSRF_TRUSTED_ORIGINS` должен содержать https://ваш-домен.onrender.com

### Ошибка 500 (Internal Server Error)
**Решение**:
1. Откройте Shell в Render
2. Проверьте логи: `render logs`
3. Выполните миграции вручную:
   ```bash
   python manage.py migrate --noinput
   ```

### Статические файлы не загружаются (404)
**Решение**:
1. Пересобрать статику:
   ```bash
   python manage.py collectstatic --noinput --clear
   ```
2. Перезагрузить приложение в Render Dashboard

### Проблема с подключением к БД
**Решение**:
1. Убедитесь, что PostgreSQL добавлена как сервис (не только переменная)
2. Проверьте, что `DATABASE_URL` установлена
3. Перезагрузите сервис

---

## Дополнительные команды Render CLI

```bash
# Установка (если не установлен)
npm install -g @render/cli

# Логин
render login

# Посмотреть логи
render logs --service-id=YOUR_SERVICE_ID

# Очистить кэш и пересобрать
render deploy --service-id=YOUR_SERVICE_ID --clear-cache
```

---

## Локальное тестирование перед деплоем

```bash
# Создать .env файл для локального тестирования
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Запустить collectstatic
python manage.py collectstatic --noinput

# Запустить миграции
python manage.py migrate

# Локально запустить gunicorn
gunicorn musicrate.wsgi:application --bind 0.0.0.0:8000
```

---

## Автоматический деплой

Render будет автоматически деплоить каждый push на `main` ветку. 
Если нужен manual deploy:
1. Перейдите в **Web Service**
2. Нажмите **"Manual Deploy"** → **"Deploy latest commit"**



## Тарифы Railway

- **Бесплатно:** $5 кредитов в месяц
- **Стандарт:** $5/месяц (безлимитные кредиты)

Для небольшого проекта хватит бесплатного тарифа (~$0.023/час за веб-сервер + ~$0.013/час за БД).

---

## Troubleshooting

### Ошибка "Healthcheck failed"
- Проверьте логи: `railway logs`
- Убедитесь, что миграции прошли успешно

### Ошибка базы данных
- Проверьте, что PostgreSQL запущен
- Убедитесь, что `DATABASE_URL` установлен

### Статика не загружается
- Проверьте, что `collectstatic` прошёл успешно
- Очистите кэш браузера (Ctrl+F5)