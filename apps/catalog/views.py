from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Release
from .services import YandexMusicProvider


def index_view(request):
    releases = Release.objects.select_related('artist').all()[:24]
    context = {
        'releases': releases,
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
    results = []
    
    if query:
        provider = YandexMusicProvider()
        results = provider.search(query)
    
    if request.headers.get('HX-Request'):
        return render(request, 'catalog/partials/search_results.html', {
            'results': results,
            'query': query
        })
    
    return render(request, 'catalog/search.html', {
        'results': results,
        'query': query
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
