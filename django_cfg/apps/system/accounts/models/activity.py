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

    # Where the request came from, per request.geo (django_visitor_geo): blank when unknown or not allowed by
    # visitor_geo.level. Columns, not JSON, so "logins from GE" is a plain filter.
    country = models.CharField(max_length=2, blank=True, default="", db_index=True, help_text="ISO 3166-1 alpha-2")
    region_code = models.CharField(max_length=10, blank=True, default="")
    city = models.CharField(max_length=120, blank=True, default="", help_text="Only when visitor_geo.level is city")
    timezone = models.CharField(max_length=64, blank=True, default="")
    edge_trusted = models.BooleanField(
        default=False, help_text="The request came through the trusted edge (Cloudflare); the IP and country are real",
    )

    # Related objects (generic foreign key could be used here)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=50, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"
