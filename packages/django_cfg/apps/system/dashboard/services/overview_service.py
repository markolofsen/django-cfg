"""
Overview Service

Provides overview data including recent users and activity tracking.
Extracted from django_dashboard for API-based dashboard.
"""

import logging
from datetime import timedelta
from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)


class OverviewService:
    """
    Service for dashboard overview data.

    %%PRIORITY:HIGH%%
    %%AI_HINT: Provides recent activity and user registration tracking%%

    TAGS: overview, dashboard, activity, service
    DEPENDS_ON: [django.contrib.auth]
    """

    def __init__(self):
        """Initialize overview service."""
        self.logger = logger

    def _get_user_model(self):
        """Get the user model safely."""
        return get_user_model()

    def get_recent_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent users for activity section.

        Args:
            limit: Maximum number of users to return (default: 10)

        Returns:
            List of user dictionaries with id, username, email, is_active, date_joined

        %%AI_HINT: Real Django ORM query for recent users%%
        """
        try:
            User = self._get_user_model()
            recent_users = User.objects.order_by('-date_joined')[:limit]

            return [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email or '',
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                }
                for user in recent_users
            ]
        except Exception as e:
            self.logger.error(f"Error getting recent users: {e}")
            return []

    def get_activity_tracker(self, days: int = 365) -> List[Dict[str, Any]]:
        """
        Get activity tracker data for GitHub-style heatmap.

        Returns list of dicts with date and count for last N days.

        Args:
            days: Number of days to track (default: 365)

        Returns:
            List of activity data: [{'date': 'YYYY-MM-DD', 'count': int, 'level': int}, ...]
            level: 0-4 (0=no activity, 4=very high activity)

        %%AI_HINT: Generates daily activity counts from user registrations and logins%%
        """
        try:
            User = self._get_user_model()
            today = timezone.now().date()
            activity_data = []

            for days_ago in range(days - 1, -1, -1):  # Newest last
                date = today - timedelta(days=days_ago)

                # Count user registrations on this day
                registrations = User.objects.filter(
                    date_joined__date=date
                ).count()

                # Count logins on this day (if last_login exists)
                logins = 0
                if hasattr(User, 'last_login'):
                    logins = User.objects.filter(
                        last_login__date=date
                    ).count()

                # Total activity for the day
                total_activity = registrations + logins

                activity_data.append({
                    'date': date.isoformat(),
                    'count': total_activity,
                    'level': self._get_activity_level(total_activity),
                })

            return activity_data

        except Exception as e:
            self.logger.error(f"Error getting activity tracker: {e}")
            return []

    def _get_activity_level(self, count: int) -> int:
        """
        Convert activity count to level (0-4) for heatmap colors.

        Args:
            count: Number of activities

        Returns:
            Activity level (0-4):
            - 0 = no activity (gray)
            - 1 = low (light green)
            - 2 = medium (green)
            - 3 = high (dark green)
            - 4 = very high (darkest green)
        """
        if count == 0:
            return 0
        elif count <= 2:
            return 1
        elif count <= 5:
            return 2
        elif count <= 10:
            return 3
        else:
            return 4

    def get_key_stats(self) -> Dict[str, Any]:
        """
        Get key statistics for overview.

        Returns:
            Dictionary with users, databases, apps counts

        %%AI_HINT: Provides high-level system statistics%%
        """
        try:
            User = self._get_user_model()

            # Get database count
            from django.db import connection
            db_count = len(connection.settings_dict.get('DATABASES', {})) if hasattr(connection, 'settings_dict') else 1

            # Get app count
            from django.apps import apps
            app_count = len(apps.get_app_configs())

            return {
                'users': User.objects.count(),
                'databases': db_count,
                'apps': app_count,
            }
        except Exception as e:
            self.logger.error(f"Error getting key stats: {e}")
            return {
                'users': 0,
                'databases': 0,
                'apps': 0,
                'error': str(e)
            }

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.

        Returns:
            Dictionary with Python version and system metrics

        %%AI_HINT: System-level information using psutil%%
        """
        import sys
        import psutil

        try:
            return {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'cpu_percent': round(psutil.cpu_percent(interval=0.1), 1),
                'memory_percent': round(psutil.virtual_memory().percent, 1),
                'disk_percent': round(psutil.disk_usage('/').percent, 1),
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'error': str(e)
            }
