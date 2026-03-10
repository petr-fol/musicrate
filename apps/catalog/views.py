from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from .models import Release, Artist
from .services import YandexMusicProvider

User = get_user_model()


def index_view(request):
    releases = Release.objects.select_related('artist').all()[:24]
    
    # Рекомендации для авторизованных пользователей
    recommended_releases = []
    if request.user.is_authenticated:
        from .services import get_user_recommendations
        recommended_releases = get_user_recommendations(request.user)
    
    context = {
        'releases': releases,
        'recommended_releases': recommended_releases,
    }
    return render(request, 'catalog/index.html', context)


def release_detail_view(request, slug):
    release = get_object_or_404(
        Release.objects.select_related('artist'),
        slug=slug
    )
    reviews = release.reviews.select_related('user').all()
    
    # Calculate average criteria for radar chart
    if reviews.exists():
        avg_rhymes = sum(r.rhymes for r in reviews) / reviews.count()
        avg_structure = sum(r.structure for r in reviews) / reviews.count()
        avg_style = sum(r.style for r in reviews) / reviews.count()
        avg_charisma = sum(r.charisma for r in reviews) / reviews.count()
        avg_atmosphere = sum(r.atmosphere for r in reviews) / reviews.count()
    else:
        avg_rhymes = avg_structure = avg_style = avg_charisma = avg_atmosphere = 0
    
    context = {
        'release': release,
        'reviews': reviews,
        'review_count': reviews.count(),
        'avg_criteria': {
            'rhymes': round(avg_rhymes, 1),
            'structure': round(avg_structure, 1),
            'style': round(avg_style, 1),
            'charisma': round(avg_charisma, 1),
            'atmosphere': round(avg_atmosphere, 1),
        }
    }
    return render(request, 'catalog/release_detail.html', context)


def api_search_view(request):
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


@login_required
@require_POST
def import_release_view(request, yandex_id):
    provider = YandexMusicProvider()
    release = provider.import_release(yandex_id)

    if release:
        messages.success(request, f'Релиз "{release}" успешно импортирован!')
        return redirect('catalog:release_detail', slug=release.slug)
    else:
        messages.error(request, 'Не удалось импортировать релиз.')
        return redirect('catalog:api_search')


def artist_detail_view(request, slug):
    """Страница артиста со списком всех релизов"""
    artist = get_object_or_404(Artist, slug=slug)
    releases = artist.releases.select_related('artist').order_by('-release_date', '-created_at')
    
    # Группируем релизы по типу
    albums = releases.filter(release_type='album')
    eps = releases.filter(release_type='ep')
    singles = releases.filter(release_type='single')
    
    # Считаем общую статистику
    total_releases = releases.count()
    total_reviews = sum(r.reviews.count() for r in releases)
    
    context = {
        'artist': artist,
        'releases': releases,
        'albums': albums,
        'eps': eps,
        'singles': singles,
        'total_releases': total_releases,
        'total_reviews': total_reviews,
    }
    return render(request, 'catalog/artist_detail.html', context)
