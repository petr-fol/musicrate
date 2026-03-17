# Catalog app - views

from .index import index_view
from .release import release_detail_view
from .search import api_search_view
from .artist import artist_detail_view
from .import_views import import_release_view

__all__ = [
    'index_view',
    'release_detail_view',
    'api_search_view',
    'artist_detail_view',
    'import_release_view',
]
