from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.utils.translation import activate
from django.conf import settings


@require_POST
def set_language(request):
    """
    Установить язык для пользователя.

    Язык сохраняется в сессии и cookie.
    """
    lang_code = request.POST.get('language')
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))

    if lang_code and lang_code in [lang[0] for lang in settings.LANGUAGES]:
        # Сохраняем язык в сессии
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code

        # Активируем язык
        activate(lang_code)

        response = redirect(next_url)
        response.set_cookie(
            'django_language',
            lang_code,
            max_age=365*24*60*60,
            httponly=True,
            samesite='Lax'
        )

        return response

    return redirect(next_url)
