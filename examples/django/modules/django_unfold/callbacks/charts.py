"""
Charts data callbacks.
"""

import logging
import random
from typing import Dict, Any, List
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models.dashboard import ChartData, ChartDataset

logger = logging.getLogger(__name__)


class ChartsCallbacks:
    """Charts data callbacks."""
    
    def _get_user_model(self):
        """Get the user model safely."""
        return get_user_model()
    
    def _get_empty_chart_data(self, label: str) -> Dict[str, Any]:
        """Get empty chart data structure."""
        return ChartData(
            labels=["No Data"],
            datasets=[
                ChartDataset(
                    label=label,
                    data=[0],
                    backgroundColor="rgba(156, 163, 175, 0.1)",
                    borderColor="rgb(156, 163, 175)",
                    tension=0.4
                )
            ]
        ).model_dump()
    
    def get_user_registration_chart_data(self) -> Dict[str, Any]:
        """Get user registration chart data."""
        try:
            # Avoid database access during app initialization
            from django.apps import apps
            if not apps.ready:
                return self._get_empty_chart_data("New Users")
                
            User = self._get_user_model()
            
            # Get last 7 days of registration data
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
            
            # Generate date range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)
            
            # Get registration counts by date
            registration_data = (
                User.objects.filter(date_joined__date__gte=start_date)
                .extra({'date': "date(date_joined)"})
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )
            
            # Create data dictionary for easy lookup
            data_dict = {item['date']: item['count'] for item in registration_data}
            
            # Build chart data
            labels = [date.strftime("%m/%d") for date in date_range]
            data_points = [data_dict.get(date, 0) for date in date_range]
            
            chart_data = ChartData(
                labels=labels,
                datasets=[
                    ChartDataset(
                        label="New Users",
                        data=data_points,
                        backgroundColor="rgba(59, 130, 246, 0.1)",
                        borderColor="rgb(59, 130, 246)",
                        tension=0.4
                    )
                ]
            )
            
            return chart_data.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting user registration chart data: {e}")
            return self._get_empty_chart_data("New Users")

    def get_user_activity_chart_data(self) -> Dict[str, Any]:
        """Get user activity chart data."""
        try:
            # Avoid database access during app initialization
            from django.apps import apps
            if not apps.ready:
                return self._get_empty_chart_data("Active Users")
                
            User = self._get_user_model()
            
            # Get activity data for last 7 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
            
            # Generate date range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)
            
            # Get login activity (users who logged in each day)
            activity_data = (
                User.objects.filter(last_login__date__gte=start_date, last_login__isnull=False)
                .extra({'date': "date(last_login)"})
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )
            
            # Create data dictionary for easy lookup
            data_dict = {item['date']: item['count'] for item in activity_data}
            
            # Build chart data
            labels = [date.strftime("%m/%d") for date in date_range]
            data_points = [data_dict.get(date, 0) for date in date_range]
            
            chart_data = ChartData(
                labels=labels,
                datasets=[
                    ChartDataset(
                        label="Active Users",
                        data=data_points,
                        backgroundColor="rgba(34, 197, 94, 0.1)",
                        borderColor="rgb(34, 197, 94)",
                        tension=0.4
                    )
                ]
            )
            
            return chart_data.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting user activity chart data: {e}")
            return self._get_empty_chart_data("Active Users")
    
    def get_activity_tracker_data(self) -> List[Dict[str, str]]:
        """Get activity tracker data for the last 52 weeks (GitHub-style)."""
        try:
            # Avoid database access during app initialization
            from django.apps import apps
            if not apps.ready:
                return self._get_empty_tracker_data()
                
            User = self._get_user_model()
            
            # Get data for last 52 weeks (365 days)
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=364)  # 52 weeks * 7 days - 1
            
            # Get activity data by date
            activity_data = (
                User.objects.filter(last_login__date__gte=start_date, last_login__isnull=False)
                .extra({'date': "date(last_login)"})
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
                
                # Determine color based on activity level
                if activity_count == 0:
                    color = "bg-base-200 dark:bg-base-700"
                    level = "No activity"
                elif activity_count <= 2:
                    color = "bg-green-200 dark:bg-green-800"
                    level = "Low activity"
                elif activity_count <= 5:
                    color = "bg-green-400 dark:bg-green-600"
                    level = "Medium activity"
                elif activity_count <= 10:
                    color = "bg-green-600 dark:bg-green-500"
                    level = "High activity"
                else:
                    color = "bg-green-800 dark:bg-green-400"
                    level = "Very high activity"
                
                tracker_data.append({
                    "color": color,
                    "tooltip": f"{current_date.strftime('%Y-%m-%d')}: {activity_count} active users ({level})"
                })
                
                current_date += timedelta(days=1)
            
            return tracker_data
            
        except Exception as e:
            logger.error(f"Error getting activity tracker data: {e}")
            return self._get_empty_tracker_data()
    
    def _get_empty_tracker_data(self) -> List[Dict[str, str]]:
        """Get empty tracker data (365 days of no activity)."""
        tracker_data = []
        for i in range(365):
            tracker_data.append({
                "color": "bg-base-200 dark:bg-base-700",
                "tooltip": f"Day {i + 1}: No data available"
            })
        return tracker_data
