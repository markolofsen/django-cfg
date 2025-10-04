"""
Registration and source tracking models.
"""

from django.db import models
from urllib.parse import urlparse


class RegistrationSource(models.Model):
    """Model for tracking user registration sources/projects."""
    url = models.URLField(unique=True, help_text="Source URL (e.g., https://unrealon.com)")
    name = models.CharField(max_length=100, blank=True, help_text="Display name for the source")
    description = models.TextField(blank=True, help_text="Optional description")
    is_active = models.BooleanField(default=True, help_text="Whether this source is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.get_domain()

    def get_domain(self):
        """Extract domain from URL."""
        try:
            parsed = urlparse(self.url)
            return parsed.netloc
        except:
            return self.url

    def get_display_name(self):
        """Get display name or domain."""
        return self.name or self.get_domain()

    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = "Registration Source"
        verbose_name_plural = "Registration Sources"
        ordering = ['-created_at']


class UserRegistrationSource(models.Model):
    """Many-to-many relationship between users and registration sources."""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='user_registration_sources')
    source = models.ForeignKey(RegistrationSource, on_delete=models.CASCADE, related_name='user_registration_sources')
    first_registration = models.BooleanField(default=True, help_text="Whether this was the first registration from this source")
    registration_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'django_cfg_accounts'
        unique_together = ['user', 'source']
        verbose_name = "User Registration Source"
        verbose_name_plural = "User Registration Sources"
        ordering = ['-registration_date']
