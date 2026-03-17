from django.urls import path
from . import views

app_name = 'themes'

urlpatterns = [
    path('set/', views.set_theme, name='set_theme'),
    path('available/', views.get_available_themes, name='available_themes'),
]
