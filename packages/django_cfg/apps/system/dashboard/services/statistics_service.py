"""
Statistics Service

Collects and aggregates statistics for dashboard display.
Uses Django ORM for real data collection.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)


class StatisticsService:
    """
    Service for collecting dashboard statistics.

    %%PRIORITY:HIGH%%
    %%AI_HINT: This service collects data from various Django models using ORM%%

    TAGS: statistics, dashboard, service
    """

    def __init__(self):
        """Initialize statistics service."""
        self.logger = logger

    def _get_user_model(self):
        """Get the user model safely."""
        return get_user_model()

    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user-related statistics.

        Returns:
            Dictionary containing user stats:
            - total_users: Total number of users
            - active_users: Number of active users
            - new_users: New users in last 7 days
            - superusers: Number of superusers

        %%AI_HINT: Uses real Django ORM queries from User model%%
        """
        try:
            User = self._get_user_model()

            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            new_users_7d = User.objects.filter(
                date_joined__gte=timezone.now() - timedelta(days=7)
            ).count()
            superusers = User.objects.filter(is_superuser=True).count()

            return {
                'total_users': total_users,
                'active_users': active_users,
                'new_users': new_users_7d,
                'superusers': superusers,
            }
        except Exception as e:
            self.logger.error(f"Error getting user statistics: {e}", exc_info=True)
            return {
                'total_users': 0,
                'active_users': 0,
                'new_users': 0,
                'superusers': 0,
                'error': str(e)
            }

    def get_app_statistics(self) -> Dict[str, Any]:
        """
        Get application-specific statistics.

        Returns:
            Dictionary with aggregated app statistics.
            {
                'apps': {app_label: {...stats...}},
                'total_records': int,
                'total_models': int,
                'total_apps': int
            }

        %%AI_HINT: Real app introspection using Django apps registry%%
        """
        try:
            stats = {"apps": {}, "total_records": 0, "total_models": 0, "total_apps": 0}

            # Get all installed apps
            for app_config in apps.get_app_configs():
                app_label = app_config.label

                # Skip system apps
                if app_label in ["admin", "contenttypes", "sessions", "auth"]:
                    continue

                app_stats = self._get_app_stats(app_label)
                if app_stats:
                    stats["apps"][app_label] = app_stats
                    stats["total_records"] += app_stats.get("total_records", 0)
                    stats["total_models"] += app_stats.get("model_count", 0)
                    stats["total_apps"] += 1

            return stats
        except Exception as e:
            self.logger.error(f"Error getting app statistics: {e}")
            return {'apps': {}, 'total_records': 0, 'total_models': 0, 'total_apps': 0, 'error': str(e)}

    def _get_app_stats(self, app_label: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific app."""
        try:
            app_config = apps.get_app_config(app_label)
            # Convert generator to list to avoid len() error
            models_list = list(app_config.get_models())

            if not models_list:
                return None

            app_stats = {
                "name": app_config.verbose_name or app_label.title(),
                "models": [],
                "total_records": 0,
                "model_count": len(models_list),
            }

            for model in models_list:
                try:
                    # Get model statistics
                    model_stats = self._get_model_stats(model)
                    if model_stats:
                        # Add model_name to the stats dict
                        model_stats["model_name"] = model._meta.model_name
                        app_stats["models"].append(model_stats)
                        app_stats["total_records"] += model_stats.get("count", 0)
                except Exception:
                    continue

            return app_stats

        except Exception:
            return None

    def _get_model_stats(self, model) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific model."""
        from django.db import OperationalError, ProgrammingError

        try:
            # Just try to count - if table doesn't exist, exception will be caught
            count = model.objects.count()

            # Get basic model info
            model_stats = {
                "name": model._meta.verbose_name_plural
                or model._meta.verbose_name
                or model._meta.model_name,
                "count": count,
                "fields_count": len(model._meta.fields),
                "admin_url": f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist",
            }

            return model_stats

        except (OperationalError, ProgrammingError):
            # Table doesn't exist or other DB error - skip this model silently
            return None
        except Exception:
            # Any other error - skip this model silently
            return None

    def get_stat_cards(self) -> List[Dict[str, Any]]:
        """
        Get statistics cards for dashboard overview.

        Returns:
            List of stat card dictionaries ready for serialization.
            Each card contains: title, value, icon, change, change_type

        USED_BY: DashboardViewSet.overview endpoint
        %%AI_HINT: Real data from User model with calculated changes%%
        """
        try:
            user_stats = self.get_user_statistics()

            total_users = user_stats['total_users']
            active_users = user_stats['active_users']
            new_users_7d = user_stats['new_users']
            superusers = user_stats['superusers']

            cards = [
                {
                    'title': 'Total Users',
                    'value': f"{total_users:,}",
                    'icon': 'people',
                    'change': f"+{new_users_7d}" if new_users_7d > 0 else None,
                    'change_type': 'positive' if new_users_7d > 0 else 'neutral',
                    'color': 'primary',
                    'description': 'Registered users',
                },
                {
                    'title': 'Active Users',
                    'value': f"{active_users:,}",
                    'icon': 'person',
                    'change': (
                        f"{(active_users/total_users*100):.1f}%"
                        if total_users > 0
                        else "0%"
                    ),
                    'change_type': (
                        'positive' if active_users > total_users * 0.7 else 'neutral'
                    ),
                    'color': 'success',
                    'description': 'Currently active',
                },
                {
                    'title': 'New This Week',
                    'value': f"{new_users_7d:,}",
                    'icon': 'person_add',
                    'change_type': 'positive' if new_users_7d > 0 else 'neutral',
                    'color': 'info',
                    'description': 'Last 7 days',
                },
                {
                    'title': 'Superusers',
                    'value': f"{superusers:,}",
                    'icon': 'admin_panel_settings',
                    'change': (
                        f"{(superusers/total_users*100):.1f}%" if total_users > 0 else "0%"
                    ),
                    'change_type': 'neutral',
                    'color': 'warning',
                    'description': 'Administrative access',
                },
            ]

            return cards

        except Exception as e:
            self.logger.error(f"Error generating stat cards: {e}")
            return []

    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent activity entries for dashboard.

        Args:
            limit: Maximum number of activity entries to return

        Returns:
            List of recent activity entries

        %%AI_HINT: Returns placeholder - connect to django-auditlog when available%%
        """
        try:
            # Note: This is a placeholder. Real implementation should connect to:
            # - django-auditlog (if installed)
            # - Custom activity/history tracking
            # - Django admin logs (LogEntry model)

            # Try to get Django admin logs as fallback
            from django.contrib.admin.models import LogEntry

            activities = []
            log_entries = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:limit]

            for entry in log_entries:
                activities.append({
                    'id': entry.pk,
                    'user': entry.user.get_username() if entry.user else 'System',
                    'action': entry.get_action_flag_display().lower(),
                    'resource': str(entry),
                    'timestamp': entry.action_time.isoformat(),
                    'icon': self._get_activity_icon(entry.action_flag),
                    'color': self._get_activity_color(entry.action_flag),
                })

            return activities

        except Exception as e:
            self.logger.error(f"Error getting recent activity: {e}")
            return []

    def _get_activity_icon(self, action_flag: int) -> str:
        """Get icon for activity based on action flag."""
        icons = {
            1: 'add_circle',      # ADDITION
            2: 'edit',            # CHANGE
            3: 'delete',          # DELETION
        }
        return icons.get(action_flag, 'circle')

    def _get_activity_color(self, action_flag: int) -> str:
        """Get color for activity based on action flag."""
        colors = {
            1: 'success',   # ADDITION
            2: 'primary',   # CHANGE
            3: 'error',     # DELETION
        }
        return colors.get(action_flag, 'default')

    def get_recent_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent users data.

        Args:
            limit: Maximum number of users to return

        Returns:
            List of recent user dictionaries with admin URLs

        %%AI_HINT: Real data from User model with admin URLs%%
        """
        try:
            User = self._get_user_model()
            recent_users = User.objects.select_related().order_by("-date_joined")[:limit]

            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email or "No email",
                    "date_joined": (
                        user.date_joined.strftime("%Y-%m-%d %H:%M")
                        if user.date_joined
                        else "Unknown"
                    ),
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "last_login": (
                        user.last_login.strftime("%Y-%m-%d %H:%M")
                        if user.last_login
                        else None
                    ),
                }
                for user in recent_users
            ]
        except Exception as e:
            self.logger.error(f"Error getting recent users: {e}")
            return []

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system performance metrics.

        Returns:
            Dictionary with system metrics (CPU, memory, disk, etc.)

        %%AI_HINT: Uses psutil for real system metrics when available%%
        """
        try:
            # Try to use psutil for real system metrics
            try:
                import psutil
                import time

                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)

                # Get memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent

                # Get disk usage for root partition
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent

                # Get network IO
                net_io = psutil.net_io_counters()

                # Get system uptime
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time
                uptime_days = int(uptime_seconds // 86400)
                uptime_hours = int((uptime_seconds % 86400) // 3600)

                return {
                    'cpu_usage': round(cpu_percent, 1),
                    'memory_usage': round(memory_percent, 1),
                    'disk_usage': round(disk_percent, 1),
                    'network_in': f"{net_io.bytes_recv / (1024**2):.1f} MB",
                    'network_out': f"{net_io.bytes_sent / (1024**2):.1f} MB",
                    'response_time': '< 100ms',  # Placeholder - can be calculated from middleware
                    'uptime': f"{uptime_days} days, {uptime_hours} hours",
                }
            except ImportError:
                self.logger.warning("psutil not installed, returning placeholder metrics")
                # Fallback to placeholder data if psutil not available
                return {
                    'cpu_usage': 0,
                    'memory_usage': 0,
                    'disk_usage': 0,
                    'network_in': 'N/A',
                    'network_out': 'N/A',
                    'response_time': 'N/A',
                    'uptime': 'N/A',
                }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}
