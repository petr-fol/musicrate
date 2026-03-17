from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.catalog.models import Release
from ..models import Review
from ..forms import ReviewForm


@login_required
def add_review_view(request, slug):
    """
    Добавление рецензии на релиз.
    
    Доступно только авторизованным пользователям.
    Один пользователь может оставить только одну рецензию на релиз.
    """
    release = get_object_or_404(Release, slug=slug)

    # Check if user already reviewed this release
    existing_review = Review.objects.filter(user=request.user, release=release).first()
    if existing_review:
        messages.warning(request, 'Вы уже оставляли рецензию на этот релиз.')
        return redirect('catalog:release_detail', slug=release.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.release = release
            review.save()
            messages.success(request, 'Ваша рецензия успешно добавлена!')
            return redirect('catalog:release_detail', slug=release.slug)
    else:
        form = ReviewForm()

    context = {
        'release': release,
        'form': form,
    }
    return render(request, 'reviews/add_review.html', context)
