from django.urls import path
from . import views

app_name = 'i18n'

urlpatterns = [
    path('set/', views.set_language, name='set_language'),
]
