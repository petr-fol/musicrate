from django.contrib import admin
from .models import Theme, ThemePreference


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'theme_type', 'is_default', 'is_active', 'created_at']
    list_filter = ['theme_type', 'is_default', 'is_active']
    search_fields = ['name', 'slug']
    ordering = ['is_default', 'name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'theme_type', 'is_default', 'is_active')
        }),
        ('Цвета', {
            'fields': (
                ('bg_primary', 'bg_secondary', 'bg_tertiary', 'bg_card'),
                ('text_primary', 'text_secondary', 'text_muted'),
                ('accent_primary', 'accent_hover', 'border_color'),
            )
        }),
    )


@admin.register(ThemePreference)
class ThemePreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'updated_at']
    list_filter = ['theme']
    search_fields = ['user__username', 'theme__name']
    raw_id_fields = ['user']
