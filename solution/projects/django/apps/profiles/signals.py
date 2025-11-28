"""
Signals for automatic profile management.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save the UserProfile when User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Create profile if it doesn't exist
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    """
    Automatically delete UserProfile when User is deleted.
    Note: This is usually handled by CASCADE, but kept for explicit logging.
    """
    try:
        if hasattr(instance, 'profile'):
            instance.profile.delete()
    except UserProfile.DoesNotExist:
        pass
