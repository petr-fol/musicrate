from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from ..services.yandex_music import YandexMusicProvider


@login_required
@require_POST
def import_release_view(request, yandex_id):
    """
    Импорт релиза из Яндекс.Музыки.
    
    Доступно только авторизованным пользователям.
    """
    provider = YandexMusicProvider()
    release = provider.import_release(yandex_id)

    if release:
        messages.success(request, f'Релиз "{release}" успешно импортирован!')
        return redirect('catalog:release_detail', slug=release.slug)
    else:
        messages.error(request, 'Не удалось импортировать релиз.')
        return redirect('catalog:api_search')
