from django.shortcuts import render, get_object_or_404
from ..models import Release


def release_detail_view(request, slug):
    """
    Страница детального просмотра релиза.
    
    Отображает информацию о релизе, рецензии и средние оценки по критериям.
    """
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
