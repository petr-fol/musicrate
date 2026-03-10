import os
import requests
from io import BytesIO
from datetime import datetime
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models import Count, Avg
from yandex_music import Client
from .models import Artist, Release


def get_user_recommendations(user, limit=6):
    """
    Генерирует рекомендации релизов для пользователя на основе:
    1. Артистов, которых пользователь чаще всего оценивал
    2. Предпочтений по жанрам (через оценку релизов)
    3. Новых релизов от любимых артистов
    """
    from apps.reviews.models import Review
    
    # Получаем все рецензии пользователя
    user_reviews = Review.objects.filter(user=user).select_related('release__artist')
    
    if not user_reviews.exists():
        # Если нет рецензий, возвращаем популярные релизы
        return list(Release.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-average_score', '-review_count')[:limit])
    
    # Считаем количество рецензий по артистам
    artist_counts = {}
    for review in user_reviews:
        artist = review.release.artist
        artist_counts[artist.id] = artist_counts.get(artist.id, 0) + 1
    
    # Топ-3 любимых артиста
    top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_artist_ids = [artist_id for artist_id, _ in top_artists]
    
    # Получаем релизы любимых артистов, которые пользователь ещё не оценил
    reviewed_release_ids = user_reviews.values_list('release_id', flat=True)
    
    recommended = Release.objects.filter(
        artist_id__in=top_artist_ids
    ).exclude(
        id__in=reviewed_release_ids
    ).select_related('artist').order_by('-release_date', '-created_at')[:limit]
    
    # Если недостаточно рекомендаций от любимых артистов, добавляем похожие
    if len(recommended) < limit:
        # Получаем артистов, на которых похожи любимые (через общих слушателей)
        similar_artist_ids = Artist.objects.filter(
            releases__reviews__in=user_reviews
        ).exclude(
            id__in=top_artist_ids
        ).annotate(
            review_count=Count('releases__reviews')
        ).order_by('-review_count').values_list('id', flat=True)[:5]
        
        additional = Release.objects.filter(
            artist_id__in=similar_artist_ids
        ).exclude(
            id__in=reviewed_release_ids
        ).select_related('artist').order_by('-average_score', '-release_date')[:limit - len(recommended)]
        
        recommended = list(recommended) + list(additional)
    
    return list(recommended)[:limit]


class YandexMusicProvider:
    def __init__(self):
        token = os.getenv('YANDEX_MUSIC_TOKEN', '')
        self.client = Client(token).init() if token else Client().init()

    def _parse_release_date(self, date_value):
        """Parse release date from various formats"""
        if not date_value:
            return None
        
        date_str = str(date_value)
        
        # ISO 8601 format: 2020-12-01T00:00:00+03:00
        if 'T' in date_str:
            try:
                return datetime.fromisoformat(date_str).date()
            except ValueError:
                pass
        
        # YYYY-MM-DD format
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
        
        return None

    def search(self, query, limit=10):
        """Search for releases on Yandex Music"""
        results = []
        
        try:
            search_result = self.client.search(query, type_='album')
            
            if search_result.albums:
                for album in search_result.albums.results[:limit]:
                    cover_url = None
                    if album.cover_uri:
                        cover_url = f"https://{album.cover_uri.replace('%%', '400x400')}"
                    
                    artists = ', '.join([a.name for a in album.artists])
                    
                    results.append({
                        'yandex_id': str(album.id),
                        'title': album.title,
                        'artists': artists,
                        'year': album.year,
                        'cover_url': cover_url,
                        'type': album.meta_type,
                    })
        except Exception as e:
            print(f"Search error: {e}")
        
        return results

    def import_release(self, yandex_id):
        """Import a release from Yandex Music to database"""
        try:
            album = self.client.albums_with_tracks(yandex_id)
            
            if not album:
                return None
            
            # Get first album if it's a list
            if isinstance(album, list):
                album = album[0]
            
            # Create or get artist
            artist_data = album.artists[0] if album.artists else None
            if not artist_data:
                return None
            
            artist, _ = Artist.objects.get_or_create(
                yandex_id=str(artist_data.id),
                defaults={
                    'name': artist_data.name,
                }
            )
            
            # Download artist image if available
            if artist_data.cover and not artist.image:
                artist_image_url = f"https://{artist_data.cover.uri.replace('%%', '400x400')}"
                self._download_image(artist, artist_image_url, 'image')
            
            # Determine release type
            release_type = 'album'
            if album.meta_type:
                if album.meta_type == 'single':
                    release_type = 'single'
                elif album.meta_type == 'ep':
                    release_type = 'ep'
            elif album.track_count:
                if album.track_count <= 3:
                    release_type = 'single'
                elif album.track_count <= 6:
                    release_type = 'ep'
            
            # Create or get release
            release, created = Release.objects.get_or_create(
                yandex_id=str(yandex_id),
                defaults={
                    'title': album.title,
                    'artist': artist,
                    'release_type': release_type,
                    'release_date': self._parse_release_date(album.release_date) if hasattr(album, 'release_date') else None,
                }
            )
            
            # Save to generate slug if created
            if created:
                release.save()
            
            # Download cover if available
            if album.cover_uri and not release.cover:
                cover_url = f"https://{album.cover_uri.replace('%%', '1000x1000')}"
                self._download_image(release, cover_url, 'cover')
            
            return release
            
        except Exception as e:
            print(f"Import error: {e}")
            return None

    def _download_image(self, instance, url, field_name):
        """Download image from URL and save to model field"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                
                filename = f"{instance.id}_{field_name}.jpg"
                getattr(instance, field_name).save(filename, File(img_temp), save=True)
        except Exception as e:
            print(f"Image download error: {e}")
