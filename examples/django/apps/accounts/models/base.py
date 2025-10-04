"""
Base utilities and functions for accounts models.
"""


def user_avatar_path(instance, filename):
    """Generate file path for user avatar."""
    return f"avatars/{instance.id}/{filename}"
