from django.contrib import admin
from .models import Artist, Release


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'yandex_id']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'release_type', 'release_date', 'average_score']
    list_filter = ['release_type', 'release_date']
    search_fields = ['title', 'artist__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['average_score']
