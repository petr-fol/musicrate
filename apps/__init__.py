"""
Тесты для приложения MusicRate

Запуск:
    docker-compose exec web python manage.py test
    
Запуск с покрытием:
    docker-compose exec web python manage.py test --verbosity=2
    
Запуск конкретного теста:
    docker-compose exec web python manage.py test apps.catalog.tests.test_models
"""
