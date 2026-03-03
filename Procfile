web: python manage.py migrate && gunicorn musicrate.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A musicrate worker -l info
