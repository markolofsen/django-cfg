"""
CloudflareSite model.

Simplified model for storing Cloudflare sites for synchronization and maintenance.
"""

from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from django_cfg.config import get_maintenance_url

class CloudflareSite(models.Model):
    """
    Store Cloudflare sites for synchronization and maintenance.
    
    Simplified from 30+ fields to just 11 essential fields.
    """
    
    # Basic info
    name = models.CharField(
        max_length=100,
        help_text="Friendly site name for identification"
    )
    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Domain name (e.g., vamcar.com)"
    )
    
    # Subdomains configuration
    include_subdomains = models.BooleanField(
        default=True,
        help_text="Apply maintenance rules to all subdomains (*.domain.com)"
    )
    subdomain_list = models.TextField(
        blank=True,
        help_text="Comma-separated list of specific subdomains to include (e.g., api,www,app)"
    )
    
    # Cloudflare IDs (auto-discovered during sync)
    zone_id = models.CharField(
        max_length=32,
        unique=True,
        help_text="Cloudflare Zone ID"
    )
    account_id = models.CharField(
        max_length=32,
        help_text="Cloudflare Account ID"
    )
    api_key = models.ForeignKey(
        'CloudflareApiKey',
        on_delete=models.PROTECT,
        help_text="API key to use for this site"
    )
    
    # Simple status
    maintenance_active = models.BooleanField(
        default=False,
        help_text="Whether maintenance mode is currently active"
    )
    maintenance_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL to redirect to during maintenance mode. If empty, uses default maintenance page."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this site is active in our system"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_maintenance_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When maintenance was last activated"
    )
    
    # Custom manager
    from ..managers.cloudflare_site_manager import CloudflareSiteManager
    objects = CloudflareSiteManager()
    
    class Meta:
        ordering = ['name']
        verbose_name = "Cloudflare Site"
        verbose_name_plural = "Cloudflare Sites"
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['maintenance_active']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self) -> str:
        status_emoji = "🔧" if self.maintenance_active else "🟢"
        return f"{status_emoji} {self.name} ({self.domain})"
    
    def enable_maintenance(self) -> None:
        """Enable maintenance mode for this site."""
        self.maintenance_active = True
        self.last_maintenance_at = timezone.now()
        self.save(update_fields=['maintenance_active', 'last_maintenance_at', 'updated_at'])
    
    def disable_maintenance(self) -> None:
        """Disable maintenance mode for this site."""
        self.maintenance_active = False
        self.save(update_fields=['maintenance_active', 'updated_at'])
    
    def get_maintenance_url(self) -> str:
        """Get the maintenance URL for this site."""
        if self.maintenance_url:
            return self.maintenance_url
        else:
            # Default maintenance page with site parameter
            return get_maintenance_url(self.domain)
    
    def get_domain_patterns(self) -> list[str]:
        """Get list of domain patterns for Page Rules based on subdomain configuration."""
        patterns = []
        
        if self.include_subdomains:
            # Include all subdomains with wildcard
            patterns.append(f"*{self.domain}/*")
            # Also include root domain explicitly
            patterns.append(f"{self.domain}/*")
        else:
            # Only root domain
            patterns.append(f"{self.domain}/*")
            
            # Add specific subdomains if specified
            if self.subdomain_list.strip():
                subdomains = [sub.strip() for sub in self.subdomain_list.split(',') if sub.strip()]
                for subdomain in subdomains:
                    patterns.append(f"{subdomain}.{self.domain}/*")
        
        return patterns
    
    def get_subdomain_display(self) -> str:
        """Get human-readable subdomain configuration."""
        if self.include_subdomains:
            return f"All subdomains (*.{self.domain})"
        elif self.subdomain_list.strip():
            subdomains = [sub.strip() for sub in self.subdomain_list.split(',') if sub.strip()]
            return f"Specific: {', '.join(subdomains)}.{self.domain}"
        else:
            return f"Root domain only ({self.domain})"
    
    def clean(self) -> None:
        """Validate model data."""
        super().clean()
        
        # Validate domain format
        domain_pattern = re.compile(
            r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
            r'(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        )
        if not domain_pattern.match(self.domain):
            raise ValidationError({'domain': 'Invalid domain format'})
        
        # Validate zone_id format (Cloudflare zone IDs are 32 chars)
        if len(self.zone_id) != 32:
            raise ValidationError({'zone_id': 'Zone ID must be 32 characters'})


