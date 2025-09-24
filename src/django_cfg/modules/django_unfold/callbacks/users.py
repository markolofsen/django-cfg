"""
Users data callbacks.
"""

import logging
from typing import List, Dict, Any

from django.contrib.auth import get_user_model

from .base import get_user_admin_urls

logger = logging.getLogger(__name__)


class UsersCallbacks:
    """Users data callbacks."""
    
    def _get_user_model(self):
        """Get the user model safely."""
        return get_user_model()
    
    def get_recent_users(self) -> List[Dict[str, Any]]:
        """Get recent users data for template."""
        try:
            # Avoid database access during app initialization
            from django.apps import apps
            if not apps.ready:
                return []
                
            User = self._get_user_model()
            recent_users = User.objects.select_related().order_by("-date_joined")[:10]

            # Get admin URLs for user model
            user_admin_urls = get_user_admin_urls()

            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email or "No email",
                    "date_joined": (
                        user.date_joined.strftime("%Y-%m-%d")
                        if user.date_joined
                        else "Unknown"
                    ),
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "last_login": user.last_login,
                    "admin_urls": {
                        "change": (
                            user_admin_urls["change"].format(id=user.id)
                            if user.id
                            else None
                        ),
                        "view": (
                            user_admin_urls["view"].format(id=user.id) if user.id else None
                        ),
                    },
                }
                for user in recent_users
            ]
        except Exception as e:
            logger.error(f"Error getting recent users: {e}")
            return []
