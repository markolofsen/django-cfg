"""
User activity logging service.
"""

import logging
from typing import Optional, Dict, Any
from django.utils import timezone

from ..models import CustomUser, UserActivity

logger = logging.getLogger(__name__)


class ActivityService:
    """Service for logging user activities."""

    @staticmethod
    def log_activity(
        user: CustomUser,
        activity_type: str,
        description: str = "",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        object_id: Optional[int] = None,
        object_type: Optional[str] = None,
    ) -> Optional[UserActivity]:
        """
        Log a user activity.
        
        Args:
            user: User performing the activity
            activity_type: Type of activity (login, logout, etc.)
            description: Activity description
            ip_address: IP address of the request
            user_agent: User agent string
            object_id: ID of related object (optional)
            object_type: Type of related object (optional)
            
        Returns:
            Created UserActivity instance or None if failed
        """
        try:
            activity = UserActivity.objects.create(
                user=user,
                activity_type=activity_type,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                object_id=object_id,
                object_type=object_type,
            )
            
            logger.debug(f"Logged activity '{activity_type}' for user {user.email}")
            return activity
            
        except Exception as e:
            logger.error(f"Failed to log activity '{activity_type}' for user {user.email}: {e}")
            return None

    @staticmethod
    def get_user_activities(
        user: CustomUser,
        activity_type: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """
        Get recent activities for a user.
        
        Args:
            user: User to get activities for
            activity_type: Filter by activity type (optional)
            limit: Maximum number of activities to return
            
        Returns:
            List of UserActivity instances
        """
        queryset = user.activities.all()
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
            
        return list(queryset.order_by('-created_at')[:limit])

    @staticmethod
    def get_activity_stats(user: CustomUser) -> Dict[str, Any]:
        """
        Get activity statistics for a user.
        
        Args:
            user: User to get stats for
            
        Returns:
            Dictionary with activity statistics
        """
        now = timezone.now()
        
        activities = user.activities.all()
        
        stats = {
            "total_activities": activities.count(),
            "recent_24h": activities.filter(
                created_at__gte=now - timezone.timedelta(hours=24)
            ).count(),
            "recent_7d": activities.filter(
                created_at__gte=now - timezone.timedelta(days=7)
            ).count(),
            "recent_30d": activities.filter(
                created_at__gte=now - timezone.timedelta(days=30)
            ).count(),
        }
        
        # Activity type breakdown
        activity_types = activities.values_list('activity_type', flat=True)
        type_counts = {}
        for activity_type in activity_types:
            type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
        
        stats["by_type"] = type_counts
        
        return stats

    @staticmethod
    def cleanup_old_activities(days: int = 90) -> int:
        """
        Clean up old activities older than specified days.
        
        Args:
            days: Number of days to keep activities
            
        Returns:
            Number of activities deleted
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        deleted_count, _ = UserActivity.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old activities older than {days} days")
        return deleted_count
