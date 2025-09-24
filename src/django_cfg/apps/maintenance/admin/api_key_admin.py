"""
CloudflareApiKey admin with Unfold styling.

Admin interface for managing Cloudflare API keys.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpRequest
from typing import Any

from unfold.admin import ModelAdmin
from unfold.decorators import display, action

from ..models import CloudflareApiKey


@admin.register(CloudflareApiKey)
class CloudflareApiKeyAdmin(ModelAdmin):
    """Admin interface for CloudflareApiKey model."""
    
    list_display = [
        'status_display',
        'name',
        'description_preview',
        'active_badge',
        'default_badge',
        'sites_count',
        'last_used_at',
        'created_at'
    ]
    
    list_display_links = ['name']
    
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
        ('Basic Information', {
            'fields': ['name', 'description']
        }),
        ('Cloudflare Configuration', {
            'fields': ['api_token', 'account_id'],
            'classes': ['collapse']
        }),
        ('Settings', {
            'fields': ['is_active', 'is_default']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'last_used_at'],
            'classes': ['collapse']
        }),
        ('Usage', {
            'fields': ['sites_using_key'],
            'classes': ['collapse']
        })
    ]
    
    actions = [
        'make_default_action',
        'activate_keys_action',
        'deactivate_keys_action'
    ]
    
    # Display methods
    
    @display(description="Status")
    def status_display(self, obj: CloudflareApiKey) -> str:
        """Display status with emoji."""
        if obj.is_active:
            if obj.is_default:
                return format_html('<span style="color: green;">🔑 {} (Default)</span>', obj.name)
            else:
                return format_html('<span style="color: green;">🔑 {}</span>', obj.name)
        else:
            return format_html('<span style="color: red;">🔒 {}</span>', obj.name)
    
    @display(description="Description")
    def description_preview(self, obj: CloudflareApiKey) -> str:
        """Show description preview."""
        if not obj.description:
            return "-"
        
        preview = obj.description[:50]
        if len(obj.description) > 50:
            preview += "..."
        
        return preview
    
    @display(description="Active")
    def active_badge(self, obj: CloudflareApiKey) -> str:
        """Display active status badge."""
        if obj.is_active:
            return format_html('<span class="badge badge-success">Active</span>')
        else:
            return format_html('<span class="badge badge-secondary">Inactive</span>')
    
    @display(description="Default")
    def default_badge(self, obj: CloudflareApiKey) -> str:
        """Display default status badge."""
        if obj.is_default:
            return format_html('<span class="badge badge-primary">Default</span>')
        else:
            return "-"
    
    @display(description="Sites")
    def sites_count(self, obj: CloudflareApiKey) -> str:
        """Display count of sites using this key."""
        count = obj.cloudflaresite_set.count()
        if count > 0:
            return f"{count} sites"
        return "No sites"
    
    def sites_using_key(self, obj: CloudflareApiKey) -> str:
        """Show sites using this API key."""
        sites = obj.cloudflaresite_set.all()[:10]  # Limit to 10 for display
        
        if not sites:
            return "No sites using this key"
        
        html = "<ul>"
        for site in sites:
            status_emoji = "🔧" if site.maintenance_active else "🟢"
            html += f"<li>{status_emoji} {site.name} ({site.domain})</li>"
        
        html += "</ul>"
        
        total_count = obj.cloudflaresite_set.count()
        if total_count > 10:
            html += f"<p><em>... and {total_count - 10} more sites</em></p>"
        
        return format_html(html)
    
    sites_using_key.short_description = "Sites Using This Key"
    
    # Admin Actions
    
    @action(description="🔑 Make default API key")
    def make_default_action(self, request: HttpRequest, queryset) -> None:
        """Make selected key the default."""
        if queryset.count() > 1:
            self.message_user(request, "Please select only one API key to make default.", level='error')
            return
        
        key = queryset.first()
        if key:
            # This will automatically set others to non-default via the model's save method
            key.is_default = True
            key.save()
            self.message_user(request, f"'{key.name}' is now the default API key.")
    
    @action(description="✅ Activate API keys")
    def activate_keys_action(self, request: HttpRequest, queryset) -> None:
        """Activate selected API keys."""
        count = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {count} API keys.")
    
    @action(description="❌ Deactivate API keys")
    def deactivate_keys_action(self, request: HttpRequest, queryset) -> None:
        """Deactivate selected API keys."""
        # Don't allow deactivating the default key
        default_keys = queryset.filter(is_default=True)
        if default_keys.exists():
            self.message_user(
                request, 
                "Cannot deactivate default API key. Please set another key as default first.", 
                level='error'
            )
            return
        
        count = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {count} API keys.")
