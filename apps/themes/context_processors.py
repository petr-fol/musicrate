from .models import Theme


def theme_context(request):
    """Добавляет текущую тему и доступные темы в контекст"""
    themes = Theme.objects.filter(is_active=True)
    current_theme = None

    if request.user.is_authenticated:
        # Получаем тему пользователя
        if hasattr(request.user, 'theme_preference') and request.user.theme_preference.theme:
            current_theme = request.user.theme_preference.theme
        else:
            # Тема по умолчанию
            current_theme = themes.filter(is_default=True).first()
    else:
        # Для анонимных пользователей - тема по умолчанию или первая активная
        current_theme = themes.filter(is_default=True).first() or themes.first()

    return {
        'current_theme': current_theme,
        'available_themes': themes,
    }
