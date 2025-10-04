"""
User Activity admin interface using Django Admin Utilities.

Enhanced activity tracking with Material Icons and optimized queries.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    UserDisplayConfig,
    DateTimeDisplayConfig,
    StatusBadgeConfig,
    Icons,
    display
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import UserActivity
from .filters import ActivityTypeFilter


@admin.register(UserActivity)
class UserActivityAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Enhanced admin for UserActivity model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user']
    
    list_display = [
        'user_display',
        'activity_type_display',
        'description_display',
        'ip_address_display',
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
    
    @display(description="User")
    def user_display(self, obj):
        """Enhanced user display with avatar."""
        config = UserDisplayConfig(
            show_avatar=True,
            avatar_size=20,
            show_email=False
        )
        return self.display_user_simple(obj.user, config)
    
    @display(description="Activity")
    def activity_type_display(self, obj):
        """Activity type with appropriate icons."""
        activity_icons = {
            'login': Icons.LOGIN,
            'logout': Icons.LOGOUT,
            'otp_requested': Icons.EMAIL,
            'otp_verified': Icons.VERIFIED,
            'profile_updated': Icons.EDIT,
            'registration': Icons.PERSON_ADD,
        }
        
        activity_variants = {
            'login': 'success',
            'logout': 'info',
            'otp_requested': 'warning',
            'otp_verified': 'success',
            'profile_updated': 'info',
            'registration': 'primary',
        }
        
        icon = activity_icons.get(obj.activity_type, Icons.DESCRIPTION)
        variant = activity_variants.get(obj.activity_type, 'info')
        
        config = StatusBadgeConfig(
            show_icons=True,
            icon=icon,
            custom_mappings={obj.get_activity_type_display(): variant}
        )
        
        return StatusBadge.create(
            text=obj.get_activity_type_display(),
            variant=variant,
            config=config
        )
    
    @display(description="Description")
    def description_display(self, obj):
        """Truncated description with full text in tooltip."""
        if len(obj.description) > 50:
            truncated = f"{obj.description[:47]}..."
            config = StatusBadgeConfig(show_icons=True, icon=Icons.DESCRIPTION)
            return StatusBadge.create(
                text=truncated,
                variant="secondary",
                config=config
            )
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.DESCRIPTION)
        return StatusBadge.create(
            text=obj.description,
            variant="info",
            config=config
        )
    
    @display(description="IP Address")
    def ip_address_display(self, obj):
        """IP address with network icon."""
        if not obj.ip_address:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.PUBLIC)
        return StatusBadge.create(
            text=obj.ip_address,
            variant="secondary",
            config=config
        )
    
    @display(description="When")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
