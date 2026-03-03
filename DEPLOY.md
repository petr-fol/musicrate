# 🚀 Railway Deployment Guide

## Быстрый старт

### 1. Залейте проект на GitHub

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Подключите Railway к GitHub

1. Зайдите на [railway.app](https://railway.app)
2. Войдите через GitHub
3. Нажмите **"New Project"**
4. Выберите **"Deploy from GitHub repo"**
5. Найдите репозиторий `musicrate`

### 3. Добавьте PostgreSQL

1. В проекте нажмите **"+ New"**
2. Выберите **"Database"** → **"PostgreSQL"**
3. Дождитесь запуска (2-3 минуты)

### 4. Добавьте Redis (опционально, для Celery)

1. Нажмите **"+ New"**
2. Выберите **"Redis"**
3. Railway автоматически добавит `REDIS_URL` в переменные окружения

### 5. Настройте переменные окружения

1. Перейдите в **"Variables"**
2. Добавьте:
   ```
   DEBUG=False
   SECRET_KEY=ваш-секретный-ключ-50-символов
   ALLOWED_HOSTS=*
   YANDEX_MUSIC_TOKEN=ваш-токен (если есть)
   ```

### 6. Деплой

1. Railway автоматически начнёт сборку
2. Первый деплой займёт ~5 минут
3. После завершения сайт будет доступен по ссылке вида:
   ```
   https://musicrate-production.up.railway.app
   ```

### 7. Создайте суперпользователя

1. Откройте **Deployments** → **web**
2. Нажмите **"Open Logs"**
3. В консоли Railway выполните:
   ```bash
   python manage.py createsuperuser
   ```
   
   Или локально:
   ```bash
   railway login
   railway run python manage.py createsuperuser
   ```

---

## Локальная установка Railway CLI

```bash
# Windows (PowerShell)
npm install -g @railway/cli

# Или через winget
winget install Railway.cli
```

### Команды CLI

```bash
# Войти в аккаунт
railway login

# Инициализировать проект
railway init

# Добавить переменные окружения
railway variables set DEBUG=False
railway variables set SECRET_KEY=your-secret-key

# Запустить команду на сервере
railway run python manage.py createsuperuser

# Посмотреть логи
railway logs
```

---

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
