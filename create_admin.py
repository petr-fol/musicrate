#!/usr/bin/env python
"""
Скрипт для создания superuser
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicrate.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Удалим старого админа если есть
User.objects.filter(username='admin').delete()

# Создадим нового
admin = User.objects.create_superuser(
    username='admin',
    email='admin@test.com',
    password='password123'
)

print("✅ Superuser создан:")
print(f"  Username: admin")
print(f"  Email: admin@test.com")
print(f"  Password: password123")
print(f"\nДля логина перейдите на: http://127.0.0.1:8000/admin/")
