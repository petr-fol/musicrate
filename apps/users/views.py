from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from apps.reviews.models import Review

User = get_user_model()


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    reviews = Review.objects.filter(user=user).select_related('release', 'release__artist')
    
    context = {
        'profile_user': user,
        'reviews': reviews,
        'review_count': reviews.count(),
    }
    return render(request, 'users/profile.html', context)
