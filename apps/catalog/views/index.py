from django.shortcuts import render
from django.db.models import Count
from ..models import Release
from ..services.recommendations import get_user_recommendations


def index_view(request):
    """
    Главная страница каталога с лентой релизов и рекомендациями.
    
    Для авторизованных пользователей показывает персонализированные рекомендации.
    """
    releases = Release.objects.select_related('artist').all()[:24]

    # Рекомендации для авторизованных пользователей
    recommended_releases = []
    if request.user.is_authenticated:
        recommended_releases = get_user_recommendations(request.user)

    context = {
        'releases': releases,
        'recommended_releases': recommended_releases,
    }
    return render(request, 'catalog/index.html', context)
