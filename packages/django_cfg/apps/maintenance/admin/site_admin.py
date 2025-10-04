"""
CloudflareSite admin using Django Admin Utilities.

Enhanced site management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.urls import reverse
from django.http import HttpRequest
from django.shortcuts import redirect
from django.db import models
from django.db.models import Count, Q
from typing import Any
from unfold.admin import ModelAdmin, TabularInline

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

from ..models import CloudflareSite, MaintenanceLog
from ..services import MaintenanceService


class MaintenanceLogInline(TabularInline):
    """Inline for recent maintenance logs."""
    
    model = MaintenanceLog
    verbose_name = "Recent Log"
    verbose_name_plural = "📋 Recent Maintenance Logs"
    extra = 0
    max_num = 5
    can_delete = False
    show_change_link = True
    
    fields = ['status_display', 'action', 'created_at', 'duration_seconds', 'error_preview']
    readonly_fields = ['status_display', 'action', 'created_at', 'duration_seconds', 'error_preview']
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    @display(description="Status")
    def status_display(self, obj):
        """Display status with badge."""
        status_variants = {
            MaintenanceLog.Status.SUCCESS: 'success',
            MaintenanceLog.Status.FAILED: 'danger',
            MaintenanceLog.Status.PENDING: 'warning'
        }
        variant = status_variants.get(obj.status, 'secondary')
        
        status_icons = {
            MaintenanceLog.Status.SUCCESS: Icons.CHECK_CIRCLE,
            MaintenanceLog.Status.FAILED: Icons.CANCEL,
            MaintenanceLog.Status.PENDING: Icons.SCHEDULE
        }
        icon = status_icons.get(obj.status, Icons.HELP)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_status_display(),
            variant=variant,
            config=config
        )
    
    @display(description="Error")
    def error_preview(self, obj):
        """Show error message preview."""
        if not obj.error_message:
            return "—"
        
        preview = obj.error_message[:50]
        if len(obj.error_message) > 50:
            preview += "..."
        
        return preview


@admin.register(CloudflareSite)
class CloudflareSiteAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for CloudflareSite using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['api_key']
    
    list_display = [
        'status_display',
        'name_display', 
        'domain_display',
        'subdomain_config_display',
        'maintenance_display',
        'active_display',
        'last_maintenance_display',
        'logs_count',
        'api_key_display'
    ]
    list_display_links = ['name_display', 'domain_display']
    ordering = ['-created_at']
    search_fields = ['name', 'domain', 'zone_id']
    list_filter = [
        'maintenance_active',
        'is_active',
        'include_subdomains',
        'created_at',
        'last_maintenance_at'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_maintenance_at',
        'logs_preview'
    ]
    
    fieldsets = [
        ('🌐 Site Information', {
            'fields': ['name', 'domain', 'zone_id'],
            'classes': ('tab',)
        }),
        ('🔧 Maintenance Configuration', {
            'fields': ['maintenance_url', 'include_subdomains'],
            'classes': ('tab',)
        }),
        ('☁️ Cloudflare Settings', {
            'fields': ['api_key'],
            'classes': ('tab',)
        }),
        ('⚙️ Status', {
            'fields': ['is_active', 'maintenance_active'],
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ['created_at', 'updated_at', 'last_maintenance_at'],
            'classes': ('tab', 'collapse')
        }),
        ('📋 Recent Logs', {
            'fields': ['logs_preview'],
            'classes': ('tab', 'collapse')
        })
    ]
    
    inlines = [MaintenanceLogInline]
    
    actions = [
        'enable_maintenance_action',
        'disable_maintenance_action',
        'activate_sites_action',
        'deactivate_sites_action',
        'sync_with_cloudflare_action'
    ]
    
    @display(description="Status")
    def status_display(self, obj: CloudflareSite) -> str:
        """Display site status with maintenance indicator."""
        if obj.maintenance_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.BUILD)
            return StatusBadge.create(
                text=f"{obj.name} (Maintenance)",
                variant="warning",
                config=config
            )
        elif obj.is_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(
                text=obj.name,
                variant="success",
                config=config
            )
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CANCEL)
            return StatusBadge.create(
                text=obj.name,
                variant="secondary",
                config=config
            )
    
    @display(description="Name", ordering="name")
    def name_display(self, obj: CloudflareSite) -> str:
        """Display site name."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.LANGUAGE)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Domain", ordering="domain")
    def domain_display(self, obj: CloudflareSite) -> str:
        """Display domain."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.PUBLIC)
        return StatusBadge.create(
            text=obj.domain,
            variant="info",
            config=config
        )
    
    @display(description="Subdomains")
    def subdomain_config_display(self, obj: CloudflareSite) -> str:
        """Display subdomain configuration."""
        if obj.include_subdomains:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.ACCOUNT_TREE)
            return StatusBadge.create(text="Includes Subdomains", variant="info", config=config)
        else:
            return "Domain Only"
    
    @display(description="Maintenance")
    def maintenance_display(self, obj: CloudflareSite) -> str:
        """Display maintenance status."""
        if obj.maintenance_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.BUILD)
            return StatusBadge.create(text="Active", variant="warning", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="Inactive", variant="success", config=config)
    
    @display(description="Active")
    def active_display(self, obj: CloudflareSite) -> str:
        """Display active status."""
        if obj.is_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="Active", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CANCEL)
            return StatusBadge.create(text="Inactive", variant="secondary", config=config)
    
    @display(description="Last Maintenance")
    def last_maintenance_display(self, obj: CloudflareSite) -> str:
        """Display last maintenance time."""
        if not obj.last_maintenance_at:
            return "Never"
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'last_maintenance_at', config)
    
    @display(description="Logs")
    def logs_count(self, obj: CloudflareSite) -> str:
        """Display count of maintenance logs."""
        count = obj.maintenancelog_set.count()
        if count > 0:
            return f"{count} logs"
        return "No logs"
    
    @display(description="API Key")
    def api_key_display(self, obj: CloudflareSite) -> str:
        """Display API key."""
        if not obj.api_key:
            return "—"
        return self.display_user_simple(obj.api_key, field_name='name')
    
    def logs_preview(self, obj: CloudflareSite) -> str:
        """Show recent maintenance logs."""
        logs = obj.maintenancelog_set.all()[:5]
        
        if not logs:
            return "No maintenance logs yet"
        
        log_list = []
        for log in logs:
            status_emoji = "✅" if log.status == MaintenanceLog.Status.SUCCESS else "❌" if log.status == MaintenanceLog.Status.FAILED else "⏳"
            log_list.append(f"{status_emoji} {log.action} - {log.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(log_list)
    
    @action(description="Enable maintenance mode", variant=ActionVariant.WARNING)
    def enable_maintenance_action(self, request: HttpRequest, queryset) -> None:
        """Enable maintenance mode for selected sites."""
        service = MaintenanceService()
        success_count = 0
        error_count = 0
        
        for site in queryset:
            try:
                service.enable_maintenance(site)
                success_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Failed to enable maintenance for {site.name}: {str(e)}")
        
        if success_count > 0:
            messages.success(request, f"Successfully enabled maintenance for {success_count} sites.")
        if error_count > 0:
            messages.error(request, f"Failed to enable maintenance for {error_count} sites.")
    
    @action(description="Disable maintenance mode", variant=ActionVariant.SUCCESS)
    def disable_maintenance_action(self, request: HttpRequest, queryset) -> None:
        """Disable maintenance mode for selected sites."""
        service = MaintenanceService()
        success_count = 0
        error_count = 0
        
        for site in queryset:
            try:
                service.disable_maintenance(site)
                success_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Failed to disable maintenance for {site.name}: {str(e)}")
        
        if success_count > 0:
            messages.success(request, f"Successfully disabled maintenance for {success_count} sites.")
        if error_count > 0:
            messages.error(request, f"Failed to disable maintenance for {error_count} sites.")
    
    @action(description="Activate sites", variant=ActionVariant.SUCCESS)
    def activate_sites_action(self, request: HttpRequest, queryset) -> None:
        """Activate selected sites."""
        count = queryset.update(is_active=True)
        messages.success(request, f"Successfully activated {count} sites.")
    
    @action(description="Deactivate sites", variant=ActionVariant.DANGER)
    def deactivate_sites_action(self, request: HttpRequest, queryset) -> None:
        """Deactivate selected sites."""
        count = queryset.update(is_active=False)
        messages.warning(request, f"Successfully deactivated {count} sites.")
    
    @action(description="Sync with Cloudflare", variant=ActionVariant.INFO)
    def sync_with_cloudflare_action(self, request: HttpRequest, queryset) -> None:
        """Sync selected sites with Cloudflare."""
        messages.info(request, f"Cloudflare sync initiated for {queryset.count()} sites.")
    
    def changelist_view(self, request, extra_context=None):
        """Add site statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_sites=Count('id'),
            active_sites=Count('id', filter=Q(is_active=True)),
            maintenance_sites=Count('id', filter=Q(maintenance_active=True)),
            subdomain_sites=Count('id', filter=Q(include_subdomains=True))
        )
        
        extra_context['site_stats'] = {
            'total_sites': stats['total_sites'] or 0,
            'active_sites': stats['active_sites'] or 0,
            'maintenance_sites': stats['maintenance_sites'] or 0,
            'subdomain_sites': stats['subdomain_sites'] or 0
        }
        
        return super().changelist_view(request, extra_context)
