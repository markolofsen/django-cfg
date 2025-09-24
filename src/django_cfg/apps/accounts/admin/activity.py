"""
User Activity admin configuration.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from unfold.admin import ModelAdmin

from ..models import UserActivity
from .filters import ActivityTypeFilter


@admin.register(UserActivity)
class UserActivityAdmin(ModelAdmin):
    """Enhanced admin for UserActivity model."""
    
    list_display = [
        'user_display', 
        'activity_type_display', 
        'description_short', 
        'ip_address', 
        'created_at_display'
    ]
    list_display_links = ['user_display', 'activity_type_display']
    list_filter = [ActivityTypeFilter, 'activity_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'description', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Activity', {
            'fields': ('user', 'activity_type', 'description')
        }),
        ('Related Object', {
            'fields': ('object_id', 'object_type'),
            'classes': ('collapse',),
            'description': 'Optional reference to related model instance'
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

    def user_display(self, obj):
        """Enhanced user display."""
        user = obj.user
        initials = f"{user.first_name[:1]}{user.last_name[:1]}".upper() or user.username[:2].upper()
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<div style="width: 20px; height: 20px; border-radius: 50%; background: #6c757d; '
            'color: white; display: flex; align-items: center; justify-content: center; '
            'font-weight: bold; font-size: 8px;">{}</div>'
            '<span>{}</span></div>',
            initials,
            user.get_full_name() or user.username
        )
    
    user_display.short_description = "User"

    def activity_type_display(self, obj):
        """Activity type with icons."""
        icons = {
            'login': '🔐',
            'logout': '🚪',
            'otp_requested': '📧',
            'otp_verified': '✅',
            'profile_updated': '✏️',
            'registration': '👤',
        }
        icon = icons.get(obj.activity_type, '📝')
        return format_html('{} {}', icon, obj.get_activity_type_display())
    
    activity_type_display.short_description = "Activity"

    def description_short(self, obj):
        """Truncated description."""
        if len(obj.description) > 50:
            return f"{obj.description[:47]}..."
        return obj.description
    
    description_short.short_description = "Description"

    def created_at_display(self, obj):
        """Created time with natural time."""
        return naturaltime(obj.created_at)
    
    created_at_display.short_description = "When"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
