from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
from ..models import Release, Artist
from ..services.yandex_music import YandexMusicProvider

User = get_user_model()


def api_search_view(request):
    """
    Поиск по каталогу: релизы, артисты, пользователи и Яндекс.Музыка.
    
    Поддерживает HTMX для динамической подгрузки результатов.
    """
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')  # all, releases, artists, users

    results = {'releases': [], 'artists': [], 'users': []}

    if query:
        # Поиск релизов в локальной базе
        results['releases'] = Release.objects.select_related('artist').filter(
            Q(title__icontains=query) | Q(artist__name__icontains=query)
        )[:20]

        # Поиск артистов в локальной базе
        results['artists'] = Artist.objects.filter(
            Q(name__icontains=query)
        )[:20]

        # Поиск пользователей
        results['users'] = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )[:20]

        # Поиск в Яндекс.Музыке (только если тип 'all' или 'releases')
        if search_type in ['all', 'releases']:
            provider = YandexMusicProvider()
            results['yandex_results'] = provider.search(query)
        else:
            results['yandex_results'] = []

    if request.headers.get('HX-Request'):
        return render(request, 'catalog/partials/search_results.html', {
            'results': results,
            'query': query,
            'search_type': search_type,
        })

    return render(request, 'catalog/search.html', {
        'results': results,
        'query': query,
        'search_type': search_type,
    })
