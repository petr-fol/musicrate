from django.shortcuts import render, get_object_or_404
from ..models import Artist


def artist_detail_view(request, slug):
    """
    Страница артиста со списком всех релизов.
    
    Отображает информацию об артисте и группирует релизы по типам:
    - Альбомы
    - EP
    - Синглы
    """
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
