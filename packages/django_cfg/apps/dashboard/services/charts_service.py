"""
Charts Service

Provides chart data for dashboard analytics.
Includes user registration charts, activity charts, and activity tracker.
"""

import logging
from datetime import timedelta
from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

logger = logging.getLogger(__name__)


class ChartsService:
    """
    Service for generating chart data.

    %%PRIORITY:MEDIUM%%
    %%AI_HINT: Generates time-series data for charts and activity tracking%%

    TAGS: charts, analytics, dashboard, service
    """

    def __init__(self):
        """Initialize charts service."""
        self.logger = logger

    def _get_user_model(self):
        """Get the user model safely."""
        return get_user_model()

    def _get_empty_chart_data(self, label: str) -> Dict[str, Any]:
        """Get empty chart data structure."""
        return {
            "labels": ["No Data"],
            "datasets": [
                {
                    "label": label,
                    "data": [0],
                    "backgroundColor": "rgba(156, 163, 175, 0.1)",
                    "borderColor": "rgb(156, 163, 175)",
                    "tension": 0.4
                }
            ]
        }

    def get_user_registration_chart(self, days: int = 7) -> Dict[str, Any]:
        """
        Get user registration chart data for last N days.

        Args:
            days: Number of days to include in chart (default 7)

        Returns:
            Chart.js compatible data structure

        %%AI_HINT: Real data aggregated by date from User.date_joined%%
        """
        try:
            User = self._get_user_model()

            # Get date range
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days - 1)

            # Generate date range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)

            # Get registration counts by date
            registration_data = (
                User.objects.filter(date_joined__date__gte=start_date)
                .annotate(date=TruncDate('date_joined'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )

            # Create data dictionary for easy lookup
            data_dict = {item['date']: item['count'] for item in registration_data}

            # Build chart data
            labels = [date.strftime("%m/%d") for date in date_range]
            data_points = [data_dict.get(date, 0) for date in date_range]

            return {
                "labels": labels,
                "datasets": [
                    {
                        "label": "New Users",
                        "data": data_points,
                        "backgroundColor": "rgba(59, 130, 246, 0.1)",
                        "borderColor": "rgb(59, 130, 246)",
                        "tension": 0.4,
                        "fill": True
                    }
                ]
            }

        except Exception as e:
            self.logger.error(f"Error getting user registration chart: {e}")
            return self._get_empty_chart_data("New Users")

    def get_user_activity_chart(self, days: int = 7) -> Dict[str, Any]:
        """
        Get user activity chart data for last N days.

        Args:
            days: Number of days to include in chart (default 7)

        Returns:
            Chart.js compatible data structure

        %%AI_HINT: Real data aggregated by date from User.last_login%%
        """
        try:
            User = self._get_user_model()

            # Get date range
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days - 1)

            # Generate date range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)

            # Get login activity (users who logged in each day)
            activity_data = (
                User.objects.filter(last_login__date__gte=start_date, last_login__isnull=False)
                .annotate(date=TruncDate('last_login'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )

            # Create data dictionary for easy lookup
            data_dict = {item['date']: item['count'] for item in activity_data}

            # Build chart data
            labels = [date.strftime("%m/%d") for date in date_range]
            data_points = [data_dict.get(date, 0) for date in date_range]

            return {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Active Users",
                        "data": data_points,
                        "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        "borderColor": "rgb(34, 197, 94)",
                        "tension": 0.4,
                        "fill": True
                    }
                ]
            }

        except Exception as e:
            self.logger.error(f"Error getting user activity chart: {e}")
            return self._get_empty_chart_data("Active Users")

    def get_activity_tracker(self, weeks: int = 52) -> List[Dict[str, Any]]:
        """
        Get activity tracker data (GitHub-style contribution graph).

        Args:
            weeks: Number of weeks to include (default 52)

        Returns:
            List of day objects with activity levels

        %%AI_HINT: 365 days of activity data for heatmap visualization%%
        """
        try:
            User = self._get_user_model()

            # Get data for specified weeks
            days = weeks * 7
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days - 1)

            # Get activity data by date
            activity_data = (
                User.objects.filter(last_login__date__gte=start_date, last_login__isnull=False)
                .annotate(date=TruncDate('last_login'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )

            # Create data dictionary for easy lookup
            data_dict = {item['date']: item['count'] for item in activity_data}

            # Generate tracker data for each day
            tracker_data = []
            current_date = start_date

            while current_date <= end_date:
                activity_count = data_dict.get(current_date, 0)

                # Determine level based on activity count
                if activity_count == 0:
                    level = 0
                    color = "#ebedf0"
                    intensity = "No activity"
                elif activity_count <= 2:
                    level = 1
                    color = "#9be9a8"
                    intensity = "Low"
                elif activity_count <= 5:
                    level = 2
                    color = "#40c463"
                    intensity = "Medium"
                elif activity_count <= 10:
                    level = 3
                    color = "#30a14e"
                    intensity = "High"
                else:
                    level = 4
                    color = "#216e39"
                    intensity = "Very high"

                tracker_data.append({
                    "date": current_date.isoformat(),
                    "count": activity_count,
                    "level": level,
                    "color": color,
                    "tooltip": f"{current_date.strftime('%Y-%m-%d')}: {activity_count} active users ({intensity})"
                })

                current_date += timedelta(days=1)

            return tracker_data

        except Exception as e:
            self.logger.error(f"Error getting activity tracker: {e}")
            return self._get_empty_tracker_data(weeks * 7)

    def _get_empty_tracker_data(self, days: int) -> List[Dict[str, Any]]:
        """Get empty tracker data."""
        tracker_data = []
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)
        current_date = start_date

        while current_date <= end_date:
            tracker_data.append({
                "date": current_date.isoformat(),
                "count": 0,
                "level": 0,
                "color": "#ebedf0",
                "tooltip": f"{current_date.strftime('%Y-%m-%d')}: No data"
            })
            current_date += timedelta(days=1)

        return tracker_data
