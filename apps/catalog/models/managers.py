from django.db import models
from django.db.models import Count, Avg


class ReleaseQuerySet(models.QuerySet):
    """QuerySet для релизов с дополнительными методами"""

    def with_review_stats(self):
        """Добавляет статистику по рецензиям"""
        return self.annotate(
            review_count=Count('reviews'),
            avg_score=Avg('reviews__total_score')
        )

    def recent(self, limit=24):
        """Последние добавленные релизы"""
        return self.order_by('-created_at')[:limit]

    def by_type(self, release_type):
        """Фильтр по типу релиза"""
        return self.filter(release_type=release_type)

    def with_covers(self):
        """Только релизы с обложками"""
        return self.exclude(cover__isnull=True)


class ReleaseManager(models.Manager):
    """Менеджер для модели Release"""

    def get_queryset(self):
        return ReleaseQuerySet(self.model, using=self._db)

    def recent(self, limit=24):
        return self.get_queryset().recent(limit)

    def with_review_stats(self):
        return self.get_queryset().with_review_stats()
    
    def by_type(self, release_type):
        return self.get_queryset().by_type(release_type)
    
    def with_covers(self):
        return self.get_queryset().with_covers()


class ArtistQuerySet(models.QuerySet):
    """QuerySet для артистов"""

    def with_releases_count(self):
        """Добавляет количество релизов"""
        return self.annotate(releases_count=Count('releases'))

    def has_releases(self):
        """Только артисты с релизами"""
        return self.filter(releases__isnull=False).distinct()


class ArtistManager(models.Manager):
    """Менеджер для модели Artist"""

    def get_queryset(self):
        return ArtistQuerySet(self.model, using=self._db)

    def with_releases_count(self):
        return self.get_queryset().with_releases_count()

    def has_releases(self):
        return self.get_queryset().has_releases()
