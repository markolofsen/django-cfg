"""Overview section for dashboard."""

from typing import Any, Dict, List

from .base import DataSection


class OverviewSection(DataSection):
    """
    Overview section showing key metrics and system status.
    """

    template_name = "admin/sections/overview_section.html"
    title = "System Overview"
    icon = "dashboard"

    def get_data(self) -> Dict[str, Any]:
        """Get overview data."""
        from django_cfg.core.config import get_current_config

        config = get_current_config()

        return {
            'stats': self.get_key_stats(),
            'system_health': self.get_system_health(),
            'recent_activity': self.get_recent_activity(),
        }

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add additional context for includes."""
        import json

        from django.utils.safestring import mark_safe

        context = super().get_context_data(**kwargs)

        # Get time range from kwargs (default: 7 days)
        time_range = kwargs.get('time_range', 7)

        # Add data needed by included components
        context['system_metrics'] = self.get_system_metrics()
        context['recent_users'] = self.get_recent_users()
        context['recent_users_table'] = self.get_recent_users_table()

        # Convert activity tracker to JSON for JavaScript
        activity_data = self.get_activity_tracker()
        context['activity_tracker'] = mark_safe(json.dumps(activity_data))

        context['charts'] = self.get_charts_data(days=time_range)

        # Quick actions come from kwargs (passed from callbacks)
        if 'quick_actions' in kwargs:
            context['quick_actions'] = kwargs['quick_actions']

        # Navigation for time range filter
        if 'navigation' in kwargs:
            context['navigation'] = kwargs['navigation']

        return context

    def get_key_stats(self) -> Dict[str, Any]:
        """Get key statistics."""
        from django.contrib.auth import get_user_model
        from django.db import connection

        User = get_user_model()

        # Get database count
        db_count = len(connection.settings_dict.get('DATABASES', {})) if hasattr(connection, 'settings_dict') else 1

        # Get app count
        from django.apps import apps
        app_count = len(apps.get_app_configs())

        return {
            'users': User.objects.count(),
            'databases': db_count,
            'apps': app_count,
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        import sys

        import psutil

        return {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }

    def get_recent_activity(self) -> list:
        """Get recent activity items."""
        # TODO: Implement activity tracking
        return []

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics for progress bars."""
        from django.core.cache import cache
        from django.db import connection

        metrics = {}

        # Database metrics
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                metrics["database"] = {
                    "status": "healthy",
                    "type": connection.settings_dict.get('ENGINE', 'Unknown').split('.')[-1],
                    "health_percentage": 95,
                    "description": "Connection successful",
                }
        except Exception as e:
            metrics["database"] = {
                "status": "error",
                "type": "Database",
                "health_percentage": 0,
                "description": f"Connection failed: {str(e)[:50]}",
            }

        # Cache metrics
        try:
            cache.set("health_check", "ok", 10)
            cache_result = cache.get("health_check")
            if cache_result == "ok":
                metrics["cache"] = {
                    "status": "healthy",
                    "type": "Memory Cache",
                    "health_percentage": 90,
                    "description": "Cache working properly",
                }
            else:
                metrics["cache"] = {
                    "status": "warning",
                    "type": "Memory Cache",
                    "health_percentage": 50,
                    "description": "Cache response delayed",
                }
        except Exception as e:
            metrics["cache"] = {
                "status": "error",
                "type": "Memory Cache",
                "health_percentage": 0,
                "description": f"Cache error: {str(e)[:50]}",
            }

        # Storage metrics
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            usage_percentage = (used / total) * 100
            free_percentage = 100 - usage_percentage

            # Status based on free space
            if free_percentage > 20:
                status = "healthy"
            elif free_percentage > 10:
                status = "warning"
            else:
                status = "error"

            metrics["storage"] = {
                "status": status,
                "type": "Disk Space",
                "health_percentage": int(free_percentage),  # Show free space percentage
                "description": f"{free_percentage:.1f}% free ({usage_percentage:.1f}% used)",
            }
        except Exception as e:
            metrics["storage"] = {
                "status": "error",
                "type": "Disk Space",
                "health_percentage": 0,
                "description": f"Check failed: {str(e)[:50]}",
            }

        # API metrics
        try:
            from django.urls import get_resolver
            resolver = get_resolver()
            url_patterns = list(resolver.url_patterns)

            metrics["api"] = {
                "status": "healthy",
                "type": "REST API",
                "health_percentage": 100,
                "description": f"{len(url_patterns)} URL patterns",
            }
        except Exception:
            metrics["api"] = {
                "status": "warning",
                "type": "REST API",
                "health_percentage": 50,
                "description": "Unable to count URLs",
            }

        return metrics

    def get_recent_users(self) -> List[Dict[str, Any]]:
        """Get recent users for activity section."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            recent_users = User.objects.order_by('-date_joined')[:5]
            return list(recent_users.values(
                'id', 'username', 'email', 'is_active', 'date_joined'
            ))
        except Exception:
            return []

    def get_recent_users_table(self) -> Dict[str, Any]:
        """Get recent users in table format for Unfold table component."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            recent_users = User.objects.order_by('-date_joined')[:10]

            return {
                "headers": ["Username", "Email", "Status", "Staff", "Joined"],
                "rows": [
                    [
                        user.username,
                        user.email,
                        "✅ Active" if user.is_active else "❌ Inactive",
                        "🛡️ Yes" if user.is_staff else "—",
                        user.date_joined.strftime('%Y-%m-%d %H:%M')
                    ]
                    for user in recent_users
                ]
            }
        except Exception:
            return {"headers": [], "rows": []}

    def get_activity_tracker(self) -> List[Dict[str, Any]]:
        """
        Get activity tracker data for GitHub-style heatmap.

        Returns list of dicts with date and count for last 365 days.
        """
        from datetime import timedelta

        from django.contrib.auth import get_user_model
        from django.utils import timezone

        User = get_user_model()

        try:
            # Get activity for last 365 days
            today = timezone.now().date()
            activity_data = []

            for days_ago in range(364, -1, -1):  # 365 days, newest last
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

        except Exception:
            # Return empty on error
            return []

    def _get_activity_level(self, count: int) -> int:
        """
        Convert activity count to level (0-4) for heatmap colors.

        0 = no activity (gray)
        1 = low (light green)
        2 = medium (green)
        3 = high (dark green)
        4 = very high (darkest green)
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

    def get_charts_data(self, days: int = 7) -> Dict[str, Any]:
        """Get charts data for Analytics Overview.

        Args:
            days: Number of days to include in charts (default: 7)
        """
        import json
        from datetime import datetime, timedelta

        from django.contrib.auth import get_user_model
        from django.utils import timezone

        User = get_user_model()

        try:
            # Get last N days of user registrations
            today = timezone.now().date()
            dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days-1, -1, -1)]

            # Count users registered each day
            registrations = []
            for date_str in dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                count = User.objects.filter(
                    date_joined__date=date_obj
                ).count()
                registrations.append(count)

            # Count active users each day (last login)
            activity = []
            for date_str in dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Count users who logged in that day
                count = User.objects.filter(
                    last_login__date=date_obj
                ).count() if hasattr(User, 'last_login') else 0
                activity.append(count)

            # Format for charts
            day_labels = [d.split('-')[2] for d in dates]  # Just day numbers

            # Prepare chart data structures
            user_reg_data = {
                'labels': day_labels,
                'datasets': [{
                    'label': 'New Users',
                    'data': registrations,
                    'backgroundColor': 'rgba(59, 130, 246, 0.5)',
                    'borderColor': 'rgb(59, 130, 246)',
                    'borderWidth': 2,
                }]
            }

            user_activity_data = {
                'labels': day_labels,
                'datasets': [{
                    'label': 'Active Users',
                    'data': activity,
                    'backgroundColor': 'rgba(34, 197, 94, 0.5)',
                    'borderColor': 'rgb(34, 197, 94)',
                    'borderWidth': 2,
                }]
            }

            return {
                # User Registrations chart
                'user_registrations': {
                    'labels': day_labels,
                    'datasets': [{
                        'label': 'New Users',
                        'data': registrations,
                    }]
                },
                # JSON string for Unfold chart component (NO mark_safe - let Django escape quotes)
                'user_registrations_json': json.dumps(user_reg_data),

                # User Activity chart
                'user_activity': {
                    'labels': day_labels,
                    'datasets': [{
                        'label': 'Active Users',
                        'data': activity,
                    }]
                },
                # JSON string for Unfold chart component (NO mark_safe - let Django escape quotes)
                'user_activity_json': json.dumps(user_activity_data),
            }
        except Exception:
            # Return empty chart data
            return {}
