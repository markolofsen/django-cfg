"""
Group admin interface using Django Admin Utilities.

Enhanced group management with Material Icons and user counts.
"""

from django.contrib import admin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    Icons,
    display
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge


# Unregister the default Group admin
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Enhanced admin for Group model using Django Admin Utilities."""
    
    list_display = [
        'name_display',
        'users_count_display',
        'permissions_count_display'
    ]
    list_display_links = ['name_display']
    search_fields = ['name']
    filter_horizontal = ['permissions']
    ordering = ['name']
    
    fieldsets = (
        ('Group Details', {
            'fields': ('name',)
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'classes': ('collapse',)
        }),
    )
    
    @display(description="Group Name")
    def name_display(self, obj):
        """Group name display with group icon."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.GROUP)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Users")
    def users_count_display(self, obj):
        """Count of users in this group."""
        count = obj.user_set.count()
        if count == 0:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.PEOPLE)
        return StatusBadge.create(
            text=f"{count} user{'s' if count != 1 else ''}",
            variant="info",
            config=config
        )
    
    @display(description="Permissions")
    def permissions_count_display(self, obj):
        """Count of permissions in this group."""
        count = obj.permissions.count()
        if count == 0:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.SECURITY)
            return StatusBadge.create(text="No permissions", variant="secondary", config=config)
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.SECURITY)
        return StatusBadge.create(
            text=f"{count} permission{'s' if count != 1 else ''}",
            variant="warning",
            config=config
        )
