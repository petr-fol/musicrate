from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('release/<slug:slug>/', views.release_detail_view, name='release_detail'),
    path('search/external/', views.api_search_view, name='api_search'),
    path('import/release/<str:yandex_id>/', views.import_release_view, name='import_release'),
]
