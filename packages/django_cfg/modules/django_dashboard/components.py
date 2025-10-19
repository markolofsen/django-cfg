"""
Dashboard Component Classes

Uses Unfold's Component Class system for data preprocessing.
Separates business logic from presentation templates.
"""

from typing import Any, Dict

from unfold.components import BaseComponent, register_component


@register_component
class SystemMetricsComponent(BaseComponent):
    """
    System metrics component for dashboard.

    Provides health metrics for database, cache, storage, and API.
    """

    def get_context_data(self, **kwargs):
        """Prepare system metrics data."""
        context = super().get_context_data(**kwargs)
        context.update({
            "data": self.get_system_metrics()
        })
        return context

    def get_system_metrics(self) -> Dict[str, Any]:
        """Fetch system health metrics."""
        import shutil

        from django.core.cache import cache
        from django.db import connection

        metrics = {}

        # Database Health
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                metrics["database"] = {
                    "value": 95,
                    "title": "Database Health",
                    "description": "Connection successful",
                }
        except Exception as e:
            metrics["database"] = {
                "value": 0,
                "title": "Database Health",
                "description": f"Error: {str(e)[:50]}",
            }

        # Cache Performance
        try:
            cache.set("health_check", "ok", 10)
            if cache.get("health_check") == "ok":
                metrics["cache"] = {
                    "value": 90,
                    "title": "Cache Performance",
                    "description": "Cache working properly",
                }
            else:
                metrics["cache"] = {
                    "value": 50,
                    "title": "Cache Performance",
                    "description": "Cache response delayed",
                }
        except Exception as e:
            metrics["cache"] = {
                "value": 0,
                "title": "Cache Performance",
                "description": f"Error: {str(e)[:50]}",
            }

        # Storage Space
        try:
            total, used, free = shutil.disk_usage("/")
            free_percentage = int((free / total) * 100)
            usage_percentage = 100 - free_percentage

            metrics["storage"] = {
                "value": free_percentage,
                "title": "Disk Space",
                "description": f"{free_percentage}% free ({usage_percentage}% used)",
            }
        except Exception as e:
            metrics["storage"] = {
                "value": 0,
                "title": "Disk Space",
                "description": f"Error: {str(e)[:50]}",
            }

        # API Health
        try:
            from django.urls import get_resolver
            resolver = get_resolver()
            url_patterns = list(resolver.url_patterns)

            metrics["api"] = {
                "value": 100,
                "title": "REST API",
                "description": f"{len(url_patterns)} URL patterns",
            }
        except Exception:
            metrics["api"] = {
                "value": 50,
                "title": "REST API",
                "description": "Unable to count URLs",
            }

        return metrics


@register_component
class RecentUsersComponent(BaseComponent):
    """
    Recent users table component.

    Provides formatted table data for displaying recent user registrations.
    """

    def get_context_data(self, **kwargs):
        """Prepare recent users table data."""
        context = super().get_context_data(**kwargs)

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            recent_users = User.objects.order_by('-date_joined')[:10]

            context.update({
                "data": {
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
            })
        except Exception:
            context.update({
                "data": {
                    "headers": [],
                    "rows": []
                }
            })

        return context


@register_component
class ChartsComponent(BaseComponent):
    """
    Charts data component for analytics.

    Provides chart data for user registrations and activity.
    Supports time range filtering (7/30/90 days).
    """

    def get_context_data(self, **kwargs):
        """Prepare charts data."""
        context = super().get_context_data(**kwargs)

        # Get time range from kwargs (default: 7 days)
        days = kwargs.get('days', 7)

        import json
        from datetime import datetime, timedelta

        from django.contrib.auth import get_user_model
        from django.utils import timezone

        User = get_user_model()

        try:
            # Get last N days
            today = timezone.now().date()
            dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d')
                     for i in range(days-1, -1, -1)]

            # User registrations
            registrations = []
            for date_str in dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                count = User.objects.filter(date_joined__date=date_obj).count()
                registrations.append(count)

            # User activity (last login)
            activity = []
            for date_str in dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                count = User.objects.filter(
                    last_login__date=date_obj
                ).count() if hasattr(User, 'last_login') else 0
                activity.append(count)

            # Format labels
            day_labels = [d.split('-')[2] for d in dates]

            # Chart data structures
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

            context.update({
                "data": {
                    "registrations": json.dumps(user_reg_data),
                    "activity": json.dumps(user_activity_data),
                }
            })
        except Exception:
            context.update({
                "data": {}
            })

        return context


@register_component
class ActivityTrackerComponent(BaseComponent):
    """
    Activity tracker component for GitHub-style heatmap.

    Provides 365 days of user activity data with level indicators.
    """

    def get_context_data(self, **kwargs):
        """Prepare activity tracker data."""
        context = super().get_context_data(**kwargs)

        from datetime import timedelta

        from django.contrib.auth import get_user_model
        from django.utils import timezone

        User = get_user_model()

        try:
            today = timezone.now().date()
            activity_data = []

            for days_ago in range(364, -1, -1):  # 365 days
                date = today - timedelta(days=days_ago)

                # Count registrations
                registrations = User.objects.filter(
                    date_joined__date=date
                ).count()

                # Count logins
                logins = 0
                if hasattr(User, 'last_login'):
                    logins = User.objects.filter(
                        last_login__date=date
                    ).count()

                total_activity = registrations + logins

                activity_data.append({
                    'date': date.isoformat(),
                    'count': total_activity,
                    'level': self._get_activity_level(total_activity),
                })

            context.update({
                "data": activity_data
            })
        except Exception:
            context.update({
                "data": []
            })

        return context

    def _get_activity_level(self, count: int) -> int:
        """Convert activity count to level (0-4) for heatmap colors."""
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
