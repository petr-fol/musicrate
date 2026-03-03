from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'release', 'total_score', 'created_at']
    list_filter = ['created_at', 'release__artist']
    search_fields = ['user__username', 'release__title', 'text']
    readonly_fields = ['total_score', 'created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'release', 'created_at')
        }),
        ('Оценки (1-10)', {
            'fields': ('rhymes', 'structure', 'style', 'charisma')
        }),
        ('Атмосфера (1-5)', {
            'fields': ('atmosphere',)
        }),
        ('Результат', {
            'fields': ('total_score', 'text')
        }),
    )
