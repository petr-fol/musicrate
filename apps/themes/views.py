from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from .models import Theme, ThemePreference


@require_POST
@login_required
def set_theme(request):
    """Установить тему для пользователя"""
    theme_slug = request.POST.get('theme_slug')
    theme = get_object_or_404(Theme, slug=theme_slug, is_active=True)

    # Получаем или создаем предпочтение
    preference, created = ThemePreference.objects.get_or_create(user=request.user)
    preference.theme = theme
    preference.save()

    # Если запрос от HTMX
    if request.headers.get('HX-Request'):
        return render(request, 'themes/partials/theme_switcher.html', {
            'themes': Theme.objects.filter(is_active=True),
            'current_theme': theme
        })

    messages.success(request, f'Тема "{theme.name}" установлена')
    return redirect(request.META.get('HTTP_REFERER', 'catalog:index'))


@require_GET
def get_available_themes(request):
    """Получить доступные темы (для API)"""
    themes = Theme.objects.filter(is_active=True)
    data = {
        'themes': [
            {
                'name': theme.name,
                'slug': theme.slug,
                'theme_type': theme.theme_type,
                'css_variables': theme.get_css_variables()
            }
            for theme in themes
        ]
    }
    return JsonResponse(data)
