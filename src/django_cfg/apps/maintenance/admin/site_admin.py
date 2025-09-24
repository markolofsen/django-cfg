"""
CloudflareSite admin with Unfold styling and action buttons.

Beautiful admin interface inspired by the old complex system but simplified.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect
from typing import Any

from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from unfold.enums import ActionVariant

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
        """Display status with emoji."""
        status_emoji = {
            MaintenanceLog.Status.SUCCESS: "✅",
            MaintenanceLog.Status.FAILED: "❌",
            MaintenanceLog.Status.PENDING: "⏳"
        }.get(obj.status, "❓")
        
        return format_html('{} {}', status_emoji, obj.get_status_display())
    
    @display(description="Error")
    def error_preview(self, obj):
        """Show error message preview."""
        if not obj.error_message:
            return "-"
        
        preview = obj.error_message[:50]
        if len(obj.error_message) > 50:
            preview += "..."
        
        return format_html('<span style="color: red; font-family: monospace;">{}</span>', preview)


@admin.register(CloudflareSite)
class CloudflareSiteAdmin(ModelAdmin):
    """Admin for CloudflareSite with Unfold styling and action buttons."""
    
    list_display = [
        'status_display',
        'name', 
        'domain',
        'subdomain_config_badge',
        'maintenance_badge',
        'active_badge',
        'last_maintenance_at',
        'logs_count',
        'action_buttons'
    ]
    
    list_display_links = ['name', 'domain']
    
    search_fields = ['name', 'domain', 'zone_id']
    
    list_filter = [
        'maintenance_active',
        'is_active',
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
        ('Basic Information', {
            'fields': ['name', 'domain']
        }),
        ('Subdomain Configuration', {
            'fields': ['include_subdomains', 'subdomain_list'],
            'description': 'Configure which subdomains should be affected by maintenance mode'
        }),
        ('Cloudflare Configuration', {
            'fields': ['zone_id', 'account_id', 'api_key'],
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ['maintenance_active', 'maintenance_url', 'is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'last_maintenance_at'],
            'classes': ['collapse']
        }),
        ('Recent Activity', {
            'fields': ['logs_preview'],
            'classes': ['collapse']
        })
    ]
    
    inlines = [MaintenanceLogInline]
    
    actions = [
        'enable_maintenance_action',
        'disable_maintenance_action',
        'sync_from_cloudflare_action'
    ]
    
    # Unfold action buttons
    actions_detail = [
        'sync_with_cloudflare_detail',
        'enable_maintenance_detail', 
        'disable_maintenance_detail'
    ]
    actions_list = [
        'bulk_sync_sites',
        'bulk_discover_sites'
    ]
    
    # Display methods
    
    @display(description="Status")
    @display(description="Subdomains", ordering='include_subdomains')
    def subdomain_config_badge(self, obj: CloudflareSite) -> str:
        """Display subdomain configuration with badge."""
        config = obj.get_subdomain_display()
        
        if obj.include_subdomains:
            # All subdomains
            badge_class = "badge-success"
            icon = "🌐"
        elif obj.subdomain_list.strip():
            # Specific subdomains
            badge_class = "badge-warning"  
            icon = "📋"
        else:
            # Root only
            badge_class = "badge-secondary"
            icon = "🏠"
        
        return format_html(
            '<span class="badge {}" title="{}">{} {}</span>',
            badge_class,
            config,
            icon,
            "All" if obj.include_subdomains else ("List" if obj.subdomain_list.strip() else "Root")
        )
    
    def status_display(self, obj: CloudflareSite) -> str:
        """Display status with emoji."""
        if obj.maintenance_active:
            return format_html('<span style="color: orange;">🔧 {}</span>', obj.name)
        elif obj.is_active:
            return format_html('<span style="color: green;">🟢 {}</span>', obj.name)
        else:
            return format_html('<span style="color: red;">🔴 {}</span>', obj.name)
    
    @display(description="Maintenance")
    def maintenance_badge(self, obj: CloudflareSite) -> str:
        """Display maintenance status badge."""
        if obj.maintenance_active:
            return format_html('<span class="badge badge-warning">🔧 Active</span>')
        else:
            return format_html('<span class="badge badge-success">✅ Normal</span>')
    
    @display(description="Site Active")
    def active_badge(self, obj: CloudflareSite) -> str:
        """Display active status badge."""
        if obj.is_active:
            return format_html('<span class="badge badge-success">Active</span>')
        else:
            return format_html('<span class="badge badge-secondary">Inactive</span>')
    
    @display(description="Logs")
    def logs_count(self, obj: CloudflareSite) -> str:
        """Display count of logs with link."""
        count = obj.logs.count()
        if count > 0:
            url = reverse('admin:maintenance_maintenancelog_changelist')
            return format_html(
                '<a href="{}?site__id__exact={}">{} logs</a>',
                url, obj.id, count
            )
        return "No logs"
    
    @display(description="Actions")
    def action_buttons(self, obj: CloudflareSite) -> str:
        """Display action buttons."""
        buttons = []
        
        if obj.maintenance_active:
            buttons.append(
                f'<a href="#" onclick="disableMaintenance({obj.id}, \'{obj.domain}\')" '
                f'class="button" style="background: green; color: white; margin: 2px;">Disable</a>'
            )
        else:
            buttons.append(
                f'<a href="#" onclick="enableMaintenance({obj.id}, \'{obj.domain}\')" '
                f'class="button" style="background: orange; color: white; margin: 2px;">Enable</a>'
            )
        
        buttons.append(
            f'<a href="#" onclick="syncSite({obj.id}, \'{obj.domain}\')" '
            f'class="button" style="background: blue; color: white; margin: 2px;">Sync</a>'
        )
        
        return mark_safe(' '.join(buttons))
    
    def logs_preview(self, obj: CloudflareSite) -> str:
        """Show recent logs preview."""
        recent_logs = obj.logs.all()[:5]
        if not recent_logs:
            return "No logs yet"
        
        html = "<ul>"
        for log in recent_logs:
            status_emoji = {
                MaintenanceLog.Status.SUCCESS: "✅",
                MaintenanceLog.Status.FAILED: "❌",
                MaintenanceLog.Status.PENDING: "⏳"
            }.get(log.status, "❓")
            
            html += f"<li>{status_emoji} {log.get_action_display()} - {log.created_at.strftime('%Y-%m-%d %H:%M')}"
            if log.error_message:
                html += f" <em>({log.error_message[:50]}...)</em>"
            html += "</li>"
        
        html += "</ul>"
        
        if obj.logs.count() > 5:
            url = reverse('admin:maintenance_maintenancelog_changelist')
            html += f'<a href="{url}?site__id__exact={obj.id}">View all logs →</a>'
        
        return mark_safe(html)
    
    logs_preview.short_description = "Recent Activity"
    
    # Admin Actions
    
    @action(description="🔧 Enable maintenance mode")
    def enable_maintenance_action(self, request: HttpRequest, queryset) -> None:
        """Enable maintenance for selected sites."""
        success_count = 0
        error_count = 0
        
        for site in queryset:
            try:
                service = MaintenanceService(site)
                service.enable_maintenance("Enabled via admin interface")
                success_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Failed to enable maintenance for {site.domain}: {str(e)}")
        
        if success_count:
            messages.success(request, f"Successfully enabled maintenance for {success_count} sites")
        
        if error_count:
            messages.error(request, f"Failed to enable maintenance for {error_count} sites")
    
    @action(description="🟢 Disable maintenance mode")
    def disable_maintenance_action(self, request: HttpRequest, queryset) -> None:
        """Disable maintenance for selected sites."""
        success_count = 0
        error_count = 0
        
        for site in queryset:
            try:
                service = MaintenanceService(site)
                service.disable_maintenance()
                success_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Failed to disable maintenance for {site.domain}: {str(e)}")
        
        if success_count:
            messages.success(request, f"Successfully disabled maintenance for {success_count} sites")
        
        if error_count:
            messages.error(request, f"Failed to disable maintenance for {error_count} sites")
    
    @action(description="🔄 Sync from Cloudflare")
    def sync_from_cloudflare_action(self, request: HttpRequest, queryset) -> None:
        """Sync selected sites from Cloudflare."""
        success_count = 0
        error_count = 0
        
        for site in queryset:
            try:
                service = MaintenanceService(site)
                service.sync_site_from_cloudflare()
                success_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f"Failed to sync {site.domain}: {str(e)}")
        
        if success_count:
            messages.success(request, f"Successfully synced {success_count} sites from Cloudflare")
        
        if error_count:
            messages.error(request, f"Failed to sync {error_count} sites")
    
    # Unfold detail actions (кнопки на странице отдельного объекта)
    
    @action(
        description="🔄 Sync with Cloudflare",
        url_path="sync-cloudflare",
        icon="refresh",
        variant=ActionVariant.INFO
    )
    def sync_with_cloudflare_detail(self, request, object_id):
        """Sync site with Cloudflare zones."""
        try:
            site = self.get_object(request, object_id)
            if not site:
                messages.error(request, "Site not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Use convenience function for single site sync
            from ..services import sync_site_from_cloudflare
            log_entry = sync_site_from_cloudflare(site)
            
            if log_entry.status == log_entry.Status.SUCCESS:
                messages.success(
                    request, 
                    f"Site '{site.name}' has been synchronized with Cloudflare."
                )
            else:
                messages.error(
                    request,
                    f"Failed to sync site '{site.name}': {log_entry.error_message}"
                )
            
        except Exception as e:
            messages.error(request, f"Failed to sync site: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="🔧 Enable Maintenance",
        url_path="enable-maintenance",
        icon="build",
        variant=ActionVariant.WARNING
    )
    def enable_maintenance_detail(self, request, object_id):
        """Enable maintenance mode for a site."""
        try:
            site = self.get_object(request, object_id)
            if not site:
                messages.error(request, "Site not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            service = MaintenanceService(site)
            service.enable_maintenance("Enabled via admin interface")
            
            messages.success(request, f"Maintenance mode enabled for {site.name}.")
            
        except Exception as e:
            messages.error(request, f"Failed to enable maintenance: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="✅ Disable Maintenance",
        url_path="disable-maintenance",
        icon="check_circle",
        variant=ActionVariant.SUCCESS
    )
    def disable_maintenance_detail(self, request, object_id):
        """Disable maintenance mode for a site."""
        try:
            site = self.get_object(request, object_id)
            if not site:
                messages.error(request, "Site not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            service = MaintenanceService(site)
            service.disable_maintenance()
            
            messages.success(request, f"Maintenance mode disabled for {site.name}.")
            
        except Exception as e:
            messages.error(request, f"Failed to disable maintenance: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    # Unfold list actions (кнопки над списком)
    
    @action(
        description="🔄 Sync All Sites with Cloudflare",
        icon="sync",
        variant=ActionVariant.INFO,
        url_path="bulk-sync-sites"
    )
    def bulk_sync_sites(self, request):
        """Bulk sync all sites with Cloudflare."""
        try:
            from ..models import CloudflareSite
            
            # Use manager method for bulk sync
            result = CloudflareSite.objects.bulk_sync_all()
            
            if result.get('synced', 0) > 0:
                messages.success(
                    request,
                    f"Successfully synchronized {result['synced']} sites with Cloudflare."
                )
            
            if result.get('errors', 0) > 0:
                # Show detailed error messages
                error_details = result.get('error_details', [])
                for error in error_details:
                    messages.error(request, f"Sync error: {error}")
                
                messages.warning(
                    request,
                    f"Synchronization completed with {result['errors']} errors."
                )
            
            if result.get('synced', 0) == 0 and result.get('errors', 0) == 0:
                messages.info(request, "No sites to synchronize.")
                
        except Exception as e:
            messages.error(request, f"Bulk sync failed: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="🔍 Discover New Sites",
        icon="search",
        variant=ActionVariant.SUCCESS,
        url_path="bulk-discover-sites"
    )
    def bulk_discover_sites(self, request):
        """Discover new sites from Cloudflare."""
        try:
            from ..models import CloudflareSite, CloudflareApiKey
            
            # Check if we have active API keys
            if not CloudflareApiKey.objects.filter(is_active=True).exists():
                messages.error(request, "No active API keys found. Please add Cloudflare API keys first.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Use manager method for discovery
            result = CloudflareSite.objects.discover_all_sites()
            
            if result.get('discovered', 0) > 0:
                messages.success(
                    request,
                    f"Successfully discovered {result['discovered']} new sites from Cloudflare."
                )
            else:
                messages.info(request, "No new sites discovered.")
                
            if result.get('errors', 0) > 0:
                messages.warning(request, f"Discovery completed with {result['errors']} API key errors.")
                
        except Exception as e:
            messages.error(request, f"Site discovery failed: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
