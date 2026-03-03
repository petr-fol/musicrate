import os
import requests
from io import BytesIO
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from yandex_music import Client
from .models import Artist, Release


class YandexMusicProvider:
    def __init__(self):
        token = os.getenv('YANDEX_MUSIC_TOKEN', '')
        self.client = Client(token).init() if token else Client().init()

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
                    'release_date': album.release_date if hasattr(album, 'release_date') else None,
                }
            )
            
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
