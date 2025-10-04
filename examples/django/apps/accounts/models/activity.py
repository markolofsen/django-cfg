"""
User activity tracking models.
"""

from django.db import models

from .choices import ActivityType


class UserActivity(models.Model):
    """
    User activity log.
    """
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Related objects (generic foreign key could be used here)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"
