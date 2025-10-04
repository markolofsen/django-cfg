"""
CloudflareApiKey admin using Django Admin Utilities.

Enhanced API key management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.http import HttpRequest
from django.db import models
from django.db.models import Count
from typing import Any
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import CloudflareApiKey


@admin.register(CloudflareApiKey)
class CloudflareApiKeyAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin interface for CloudflareApiKey model using Django Admin Utilities."""
    
    list_display = [
        'status_display',
        'name_display',
        'description_preview',
        'active_display',
        'default_display',
        'sites_count',
        'last_used_display',
        'created_at_display'
    ]
    list_display_links = ['name_display']
    ordering = ['-created_at']
    search_fields = ['name', 'description', 'account_id']
    list_filter = [
        'is_active',
        'is_default',
        'created_at',
        'last_used_at'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_used_at',
        'sites_using_key'
    ]
    
    fieldsets = [
        ('🔑 Basic Information', {
            'fields': ['name', 'description'],
            'classes': ('tab',)
        }),
        ('☁️ Cloudflare Configuration', {
            'fields': ['api_token', 'account_id'],
            'classes': ('tab', 'collapse')
        }),
        ('⚙️ Settings', {
            'fields': ['is_active', 'is_default'],
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ['created_at', 'updated_at', 'last_used_at'],
            'classes': ('tab', 'collapse')
        }),
        ('📊 Usage', {
            'fields': ['sites_using_key'],
            'classes': ('tab', 'collapse')
        })
    ]
    
    actions = [
        'make_default_action',
        'activate_keys_action',
        'deactivate_keys_action'
    ]
    
    @display(description="Status")
    def status_display(self, obj: CloudflareApiKey) -> str:
        """Display status with badge."""
        if obj.is_active:
            if obj.is_default:
                config = StatusBadgeConfig(show_icons=True, icon=Icons.STAR)
                return StatusBadge.create(
                    text=f"{obj.name} (Default)",
                    variant="success",
                    config=config
                )
            else:
                config = StatusBadgeConfig(show_icons=True, icon=Icons.KEY)
                return StatusBadge.create(
                    text=obj.name,
                    variant="success",
                    config=config
                )
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.LOCK)
            return StatusBadge.create(
                text=obj.name,
                variant="danger",
                config=config
            )
    
    @display(description="Name", ordering="name")
    def name_display(self, obj: CloudflareApiKey) -> str:
        """Display API key name."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.KEY)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Description")
    def description_preview(self, obj: CloudflareApiKey) -> str:
        """Show description preview."""
        if not obj.description:
            return "—"
        
        preview = obj.description[:50]
        if len(obj.description) > 50:
            preview += "..."
        
        return preview
    
    @display(description="Active")
    def active_display(self, obj: CloudflareApiKey) -> str:
        """Display active status badge."""
        if obj.is_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="Active", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CANCEL)
            return StatusBadge.create(text="Inactive", variant="secondary", config=config)
    
    @display(description="Default")
    def default_display(self, obj: CloudflareApiKey) -> str:
        """Display default status badge."""
        if obj.is_default:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.STAR)
            return StatusBadge.create(text="Default", variant="primary", config=config)
        else:
            return "—"
    
    @display(description="Sites")
    def sites_count(self, obj: CloudflareApiKey) -> str:
        """Display count of sites using this key."""
        count = obj.cloudflaresite_set.count()
        if count > 0:
            return f"{count} sites"
        return "No sites"
    
    @display(description="Last Used")
    def last_used_display(self, obj: CloudflareApiKey) -> str:
        """Display last used time."""
        if not obj.last_used_at:
            return "Never"
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'last_used_at', config)
    
    @display(description="Created")
    def created_at_display(self, obj: CloudflareApiKey) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    def sites_using_key(self, obj: CloudflareApiKey) -> str:
        """Show sites using this API key."""
        sites = obj.cloudflaresite_set.all()[:10]
        
        if not sites:
            return "No sites using this key"
        
        site_list = []
        for site in sites:
            status_emoji = "🔧" if site.maintenance_active else "🟢"
            site_list.append(f"{status_emoji} {site.name} ({site.domain})")
        
        result = "\n".join(site_list)
        
        total_count = obj.cloudflaresite_set.count()
        if total_count > 10:
            result += f"\n... and {total_count - 10} more sites"
        
        return result
    
    @action(description="Make default API key", variant=ActionVariant.PRIMARY)
    def make_default_action(self, request: HttpRequest, queryset) -> None:
        """Make selected key the default."""
        if queryset.count() > 1:
            messages.error(request, "Please select only one API key to make default.")
            return
        
        key = queryset.first()
        if key:
            key.is_default = True
            key.save()
            messages.success(request, f"'{key.name}' is now the default API key.")
    
    @action(description="Activate API keys", variant=ActionVariant.SUCCESS)
    def activate_keys_action(self, request: HttpRequest, queryset) -> None:
        """Activate selected API keys."""
        count = queryset.update(is_active=True)
        messages.success(request, f"Successfully activated {count} API keys.")
    
    @action(description="Deactivate API keys", variant=ActionVariant.DANGER)
    def deactivate_keys_action(self, request: HttpRequest, queryset) -> None:
        """Deactivate selected API keys."""
        default_keys = queryset.filter(is_default=True)
        if default_keys.exists():
            messages.error(
                request, 
                "Cannot deactivate default API key. Please set another key as default first."
            )
            return
        
        count = queryset.update(is_active=False)
        messages.warning(request, f"Successfully deactivated {count} API keys.")
    
    def changelist_view(self, request, extra_context=None):
        """Add API key statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_keys=Count('id'),
            active_keys=Count('id', filter=models.Q(is_active=True)),
            default_keys=Count('id', filter=models.Q(is_default=True))
        )
        
        extra_context['api_key_stats'] = {
            'total_keys': stats['total_keys'] or 0,
            'active_keys': stats['active_keys'] or 0,
            'default_keys': stats['default_keys'] or 0
        }
        
        return super().changelist_view(request, extra_context)
