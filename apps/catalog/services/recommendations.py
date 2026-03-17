"""
Recommendation system for users.

Generates personalized release recommendations based on user preferences.
"""

from django.db.models import Count
from apps.reviews.models import Review
from ..models import Release


def get_user_recommendations(user, limit=6):
    """
    Генерирует рекомендации релизов для пользователя на основе:
    1. Артистов, которых пользователь чаще всего оценивал
    2. Предпочтений по жанрам (через оценку релизов)
    3. Новых релизов от любимых артистов

    Args:
        user: Пользователь для которого генерируются рекомендации
        limit: Максимальное количество рекомендаций

    Returns:
        Список объектов Release
    """
    # Получаем все рецензии пользователя
    user_reviews = Review.objects.filter(user=user).select_related('release__artist')

    if not user_reviews.exists():
        # Если нет рецензий, возвращаем популярные релизы
        return list(Release.objects.annotate(
            num_reviews=Count('reviews')
        ).order_by('-average_score', '-num_reviews')[:limit])

    # Считаем количество рецензий по артистам
    artist_counts = _calculate_artist_counts(user_reviews)

    # Топ-3 любимых артиста
    top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_artist_ids = [artist_id for artist_id, _ in top_artists]

    # Получаем релизы любимых артистов, которые пользователь ещё не оценил
    reviewed_release_ids = list(user_reviews.values_list('release_id', flat=True))

    recommended = _get_releases_from_artists(top_artist_ids, reviewed_release_ids, limit)

    # Если недостаточно рекомендаций от любимых артистов, добавляем похожие
    if len(recommended) < limit:
        additional = _get_similar_artist_releases(
            user_reviews,
            top_artist_ids,
            reviewed_release_ids,
            limit - len(recommended)
        )
        recommended = list(recommended) + list(additional)

    return list(recommended)[:limit]


def _calculate_artist_counts(user_reviews):
    """
    Подсчитать количество рецензий по каждому артисту.

    Args:
        user_reviews: QuerySet рецензий пользователя

    Returns:
        Dict {artist_id: count}
    """
    artist_counts = {}
    for review in user_reviews:
        artist = review.release.artist
        artist_counts[artist.id] = artist_counts.get(artist.id, 0) + 1
    return artist_counts


def _get_releases_from_artists(artist_ids, excluded_release_ids, limit):
    """
    Получить релизы от указанных артистов, исключая оценённые.

    Args:
        artist_ids: Список ID артистов
        excluded_release_ids: Список ID релизов для исключения
        limit: Максимальное количество результатов

    Returns:
        QuerySet релизов
    """
    return Release.objects.filter(
        artist_id__in=artist_ids
    ).exclude(
        id__in=excluded_release_ids
    ).select_related('artist').order_by('-release_date', '-created_at')[:limit]


def _get_similar_artist_releases(user_reviews, top_artist_ids, excluded_release_ids, limit):
    """
    Получить релизы от похожих артистов.

    Args:
        user_reviews: QuerySet рецензий пользователя
        top_artist_ids: Список ID любимых артистов
        excluded_release_ids: Список ID релизов для исключения
        limit: Максимальное количество результатов

    Returns:
        QuerySet релизов
    """
    from ..models import Artist

    # Получаем артистов, на которых похожи любимые (через общих слушателей)
    similar_artist_ids = Artist.objects.filter(
        releases__reviews__in=user_reviews
    ).exclude(
        id__in=top_artist_ids
    ).annotate(
        review_count=Count('releases__reviews')
    ).order_by('-review_count').values_list('id', flat=True)[:5]

    return Release.objects.filter(
        artist_id__in=similar_artist_ids
    ).exclude(
        id__in=excluded_release_ids
    ).select_related('artist').order_by('-average_score', '-release_date')[:limit]
