from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review


@receiver(post_save, sender=Review)
def update_release_average_score_on_save(sender, instance, created, **kwargs):
    """Update release average score after review is saved"""
    try:
        if instance.release_id:
            instance.release.update_average_score()
    except Exception as e:
        print(f"Error updating release average score: {e}")
    
    # Update user points
    try:
        if instance.user_id:
            user = instance.user
            if created:
                user.points += 10  # Add 10 points for new review
                user.save(update_fields=['points'])
    except Exception as e:
        print(f"Error updating user points: {e}")


@receiver(post_delete, sender=Review)
def update_release_average_score_on_delete(sender, instance, **kwargs):
    """Update release average score after review is deleted"""
    try:
        if instance.release_id:
            instance.release.update_average_score()
    except Exception as e:
        print(f"Error updating release average score on delete: {e}")
    
    # Deduct user points
    try:
        if instance.user_id:
            user = instance.user
            user.points = max(0, user.points - 10)  # Remove 10 points, but not below 0
            user.save(update_fields=['points'])
    except Exception as e:
        print(f"Error updating user points on delete: {e}")
