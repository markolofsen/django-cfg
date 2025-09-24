"""
Admin interface for API key management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse
from django.shortcuts import redirect
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.enums import ActionVariant

from ..models import APIKey
from .filters import APIKeyStatusFilter, UserEmailFilter, RecentActivityFilter


@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin):
    """Admin interface for API keys."""
    
    list_display = [
        'key_display',
        'user_display',
        'name',
        'status_display',
        'usage_display',
        'last_used_display',
        'expires_display',
        'created_at_display'
    ]
    
    list_display_links = ['key_display', 'name']
    
    search_fields = [
        'name',
        'user__email',
        'user__first_name',
        'user__last_name',
        'key_value',
        'key_prefix'
    ]
    
    list_filter = [
        APIKeyStatusFilter,
        UserEmailFilter,
        RecentActivityFilter,
        'is_active',
        'created_at',
        'last_used'
    ]
    
    readonly_fields = [
        'key_value',
        'key_prefix',
        'usage_count',
        'last_used',
        'created_at',
        'key_statistics',
        'usage_history'
    ]
    
    fieldsets = [
        ('API Key Information', {
            'fields': ['name', 'user']
        }),
        ('Key Details', {
            'fields': ['key_value', 'key_prefix'],
            'classes': ['collapse']
        }),
        ('Settings', {
            'fields': ['is_active', 'expires_at']
        }),
        ('Usage Statistics', {
            'fields': ['usage_count', 'last_used', 'key_statistics'],
            'classes': ['collapse']
        }),
        ('Usage History', {
            'fields': ['usage_history'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at'],
            'classes': ['collapse']
        })
    ]
    
    actions = [
        'activate_keys',
        'deactivate_keys',
        'reset_usage'
    ]
    
    actions_detail = [
        'regenerate_key',
        'view_usage_stats',
        'deactivate_key'
    ]
    
    @display(description="API Key")
    def key_display(self, obj):
        """Display API key with masking."""
        if obj.key_value:
            masked_key = f"{obj.key_prefix}***{obj.key_value[-4:]}"
        else:
            masked_key = f"{obj.key_prefix}***"
            
        status_color = '#28a745' if obj.is_active else '#dc3545'
        status_icon = '🔑' if obj.is_active else '🔒'
        
        return format_html(
            '<span style="color: {};">{}</span> <code>{}</code>',
            status_color,
            status_icon,
            masked_key
        )
    
    @display(description="User")
    def user_display(self, obj):
        """Display user information."""
        user = obj.user
        if hasattr(user, 'avatar') and user.avatar:
            avatar_html = f'<img src="{user.avatar.url}" style="width: 20px; height: 20px; border-radius: 50%; margin-right: 6px;" />'
        else:
            initials = f"{user.first_name[:1]}{user.last_name[:1]}" if user.first_name and user.last_name else user.email[:2]
            avatar_html = f'<div style="width: 20px; height: 20px; border-radius: 50%; background: #6c757d; color: white; display: inline-flex; align-items: center; justify-content: center; font-size: 9px; margin-right: 6px;">{initials.upper()}</div>'
        
        return format_html(
            '{}<strong>{}</strong><br><small>{}</small>',
            avatar_html,
            user.get_full_name() or user.email,
            user.email
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Display status with validation check."""
        if not obj.is_active:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Inactive</span>'
            )
        
        if obj.expires_at and obj.expires_at <= obj.__class__.objects.model._get_current_time():
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Expired</span>'
            )
        
        if obj.is_valid():
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">Invalid</span>'
            )
    
    @display(description="Usage")
    def usage_display(self, obj):
        """Display usage statistics."""
        usage_count = obj.usage_count
        
        if usage_count == 0:
            color = '#6c757d'
            text = 'Never used'
        elif usage_count < 100:
            color = '#28a745'
            text = f'{usage_count} calls'
        elif usage_count < 1000:
            color = '#ffc107'
            text = f'{usage_count} calls'
        else:
            color = '#dc3545'
            text = f'{usage_count:,} calls'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    
    @display(description="Last Used")
    def last_used_display(self, obj):
        """Display last used time."""
        if obj.last_used:
            return naturaltime(obj.last_used)
        return format_html(
            '<span style="color: #6c757d;">Never</span>'
        )
    
    @display(description="Expires")
    def expires_display(self, obj):
        """Display expiration time."""
        if obj.expires_at:
            from django.utils import timezone
            if obj.expires_at <= timezone.now():
                return format_html(
                    '<span style="color: #dc3545;">Expired</span>'
                )
            else:
                return naturaltime(obj.expires_at)
        return format_html(
            '<span style="color: #6c757d;">Never</span>'
        )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Display creation date."""
        return naturaltime(obj.created_at)
    
    def key_statistics(self, obj):
        """Show API key statistics."""
        from django.utils import timezone
        
        # Calculate usage trends
        recent_usage = 0  # In real implementation, calculate from usage logs
        
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong>API Key Statistics:</strong><br>'
            '• Total Usage: <strong>{:,}</strong> calls<br>'
            '• Status: {}<br>'
            '• Valid: {}<br>'
            '• Last Used: {}<br>'
            '• Expires: {}<br>'
            '• Created: {}<br>'
            '</div>',
            obj.usage_count,
            'Active' if obj.is_active else 'Inactive',
            'Yes' if obj.is_valid() else 'No',
            naturaltime(obj.last_used) if obj.last_used else 'Never',
            naturaltime(obj.expires_at) if obj.expires_at else 'Never',
            naturaltime(obj.created_at)
        )
    
    key_statistics.short_description = "Key Statistics"
    
    def usage_history(self, obj):
        """Show usage history (placeholder for future implementation)."""
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong>Usage History:</strong><br>'
            '• Total API Calls: {:,}<br>'
            '• Last 24h: N/A<br>'
            '• Last 7 days: N/A<br>'
            '• Last 30 days: N/A<br>'
            '<br>'
            '<em>Detailed usage tracking will be implemented with analytics service.</em>'
            '</div>',
            obj.usage_count
        )
    
    usage_history.short_description = "Usage History"
    
    # Admin Actions
    
    @action(description="🔑 Regenerate API Key")
    def regenerate_key(self, request, object_id):
        """Regenerate API key."""
        api_key = self.get_object(request, object_id)
        if not api_key:
            self.message_user(request, "API key not found.", level='error')
            return redirect(request.META.get('HTTP_REFERER', '/admin/'))
        
        # Generate new key
        import secrets
        api_key.key_value = f"ak_{secrets.token_urlsafe(32)}"
        api_key.usage_count = 0  # Reset usage
        api_key.save()
        
        self.message_user(
            request,
            f"API key '{api_key.name}' has been regenerated. Usage count reset to 0.",
            level='success'
        )
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="📊 View Usage Statistics",
        icon="analytics",
        variant=ActionVariant.INFO
    )
    def view_usage_stats(self, request, object_id):
        """View detailed usage statistics."""
        api_key = self.get_object(request, object_id)
        if api_key:
            self.message_user(
                request,
                f"Usage statistics view for '{api_key.name}' would open here.",
                level='info'
            )
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="🔒 Deactivate Key",
        icon="block",
        variant=ActionVariant.WARNING
    )
    def deactivate_key(self, request, object_id):
        """Deactivate API key."""
        api_key = self.get_object(request, object_id)
        if not api_key:
            self.message_user(request, "API key not found.", level='error')
            return redirect(request.META.get('HTTP_REFERER', '/admin/'))
        
        api_key.is_active = False
        api_key.save()
        
        self.message_user(
            request,
            f"API key '{api_key.name}' has been deactivated.",
            level='warning'
        )
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    # Bulk Actions
    
    def activate_keys(self, request, queryset):
        """Activate selected API keys."""
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Successfully activated {count} API keys.",
            level='success'
        )
    
    activate_keys.short_description = "🔓 Activate selected API keys"
    
    def deactivate_keys(self, request, queryset):
        """Deactivate selected API keys."""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {count} API keys.",
            level='warning'
        )
    
    deactivate_keys.short_description = "🔒 Deactivate selected API keys"
    
    def reset_usage(self, request, queryset):
        """Reset usage count for selected API keys."""
        count = queryset.update(usage_count=0)
        self.message_user(
            request,
            f"Successfully reset usage count for {count} API keys.",
            level='info'
        )
    
    reset_usage.short_description = "🔄 Reset usage count"
