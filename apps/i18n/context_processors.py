from django.conf import settings
from django.utils.translation import get_language


def language_context(request):
    """Добавляет информацию о языке в контекст"""
    return {
        'current_language': get_language(),
        'available_languages': settings.LANGUAGES,
    }
