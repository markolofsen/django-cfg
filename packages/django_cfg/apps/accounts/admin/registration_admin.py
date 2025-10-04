"""
Registration admin interfaces using Django Admin Utilities.

Enhanced registration source management with Material Icons and optimized queries.
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

from ..models import RegistrationSource, UserRegistrationSource


@admin.register(RegistrationSource)
class RegistrationSourceAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Enhanced admin for RegistrationSource model using Django Admin Utilities."""
    
    list_display = [
        'name_display',
        'description_display',
        'is_active_display',
        'users_count_display',
        'created_at_display'
    ]
    list_display_links = ['name_display']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Source Details', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description="Name")
    def name_display(self, obj):
        """Name display with source icon."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.SOURCE)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Description")
    def description_display(self, obj):
        """Description display with info icon."""
        if not obj.description:
            return "—"
        
        # Truncate long descriptions
        description = obj.description
        if len(description) > 50:
            description = f"{description[:47]}..."
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.INFO)
        return StatusBadge.create(
            text=description,
            variant="info",
            config=config
        )
    
    @display(description="Status", label=True)
    def is_active_display(self, obj):
        """Active status display."""
        status = "Active" if obj.is_active else "Inactive"
        icon = Icons.CHECK_CIRCLE if obj.is_active else Icons.CANCEL
        variant = "success" if obj.is_active else "secondary"
        
        config = StatusBadgeConfig(
            show_icons=True,
            icon=icon,
            custom_mappings={status: variant}
        )
        
        return self.display_status_auto(
            type('obj', (), {'status': status})(),
            'status',
            config
        )
    
    @display(description="Users")
    def users_count_display(self, obj):
        """Count of users from this source."""
        count = obj.user_registration_sources.count()
        if count == 0:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.PEOPLE)
        return StatusBadge.create(
            text=f"{count} user{'s' if count != 1 else ''}",
            variant="info",
            config=config
        )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)


@admin.register(UserRegistrationSource)
class UserRegistrationSourceAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Enhanced admin for UserRegistrationSource model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user', 'source']
    
    list_display = [
        'user_display',
        'source_display',
        'registration_date_display'
    ]
    list_display_links = ['user_display', 'source_display']
    list_filter = ['source', 'registration_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'source__name']
    readonly_fields = ['registration_date']
    date_hierarchy = 'registration_date'
    ordering = ['-registration_date']
    
    fieldsets = (
        ('Registration Details', {
            'fields': ('user', 'source', 'first_registration')
        }),
        ('Timestamp', {
            'fields': ('registration_date',)
        }),
    )
    
    @display(description="User")
    def user_display(self, obj):
        """User display with avatar."""
        config = UserDisplayConfig(
            show_avatar=True,
            avatar_size=20,
            show_email=True
        )
        return self.display_user_simple(obj.user, config)
    
    @display(description="Source")
    def source_display(self, obj):
        """Source display with source icon."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.SOURCE)
        variant = "success" if obj.source.is_active else "secondary"
        
        return StatusBadge.create(
            text=obj.source.name,
            variant=variant,
            config=config
        )
    
    @display(description="Registered")
    def registration_date_display(self, obj):
        """Registration date with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'registration_date', config)
