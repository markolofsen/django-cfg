"""
Endpoint Groups Admin interface using Django Admin Utilities.

Clean endpoint group management for API access control.
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from unfold.admin import ModelAdmin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    UserDisplayConfig,
    StatusBadgeConfig,
    MoneyDisplayConfig,
    DateTimeDisplayConfig,
    Icons,
    display,
    action,
    ActionVariant
)
from django_cfg.modules.django_admin.utils.displays import (
    UserDisplay,
    MoneyDisplay,
    StatusDisplay,
    DateTimeDisplay
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models.subscriptions import EndpointGroup


@admin.register(EndpointGroup)
class EndpointGroupAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    Admin interface for EndpointGroup model.
    
    Features:
    - Endpoint group information
    - Pattern and description display
    - Status management
    - Automatic query optimization
    """
    
    # Performance optimization
    select_related_fields = []
    annotations = {}
    
    # List configuration
    list_display = [
        'name_display',
        'pattern_display',
        'description_display',
        'status_display',
        'created_at_display'
    ]
    
    list_filter = [
        'is_enabled',
        'created_at'
    ]
    
    search_fields = ['name', 'pattern', 'description']
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    # Display methods
    @display(description="Name")
    def name_display(self, obj):
        """Endpoint group name display."""
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            icon=Icons.GROUP
        )
    
    @display(description="Pattern")
    def pattern_display(self, obj):
        """Pattern display."""
        return StatusBadge.create(
            text=obj.pattern,
            variant="info",
            icon=Icons.CODE
        )
    
    @display(description="Description")
    def description_display(self, obj):
        """Description display."""
        if obj.description:
            # Truncate long descriptions
            desc = obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
            return desc
        return "—"
    
    @display(description="Status")
    def status_display(self, obj):
        """Status display."""
        if obj.is_enabled:
            status = "Enabled"
            variant = "success"
            icon = Icons.CHECK_CIRCLE
        else:
            status = "Disabled"
            variant = "danger"
            icon = Icons.CANCEL
        
        return StatusBadge.create(
            text=status,
            variant=variant,
            icon=icon
        )
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created at display."""
        config = DateTimeDisplayConfig(
            show_relative=True,
            show_absolute=True
        )
        return self.display_datetime_relative(obj, 'created_at', config)
