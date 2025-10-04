"""
API Keys Admin interface using Django Admin Utilities.

Clean API key management with security features.
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
    DateTimeDisplayConfig,
    Icons,
    display,
    action,
    ActionVariant
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge
from django_cfg.modules.django_logging import get_logger

from ..models import APIKey

logger = get_logger("api_keys_admin")


@admin.register(APIKey)
class APIKeyAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """
    APIKey admin using Django Admin Utilities.
    
    Features:
    - Secure API key display
    - Usage tracking
    - Activity monitoring
    - Clean utilities integration
    """
    
    # Performance optimization
    select_related_fields = ['user']
    annotations = {}
    # Note: Annotations disabled until proper usage tracking is implemented
    # 'usage_count': Count('usage_logs') or similar
    
    # List configuration
    list_display = [
        'key_display',
        'user_display',
        'name_display',
        'status_display',
        'usage_display',
        'created_display'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'last_used_at'
    ]
    
    search_fields = [
        'name',
        'user__username',
        'user__email',
        'key'  # Be careful with this in production
    ]
    
    readonly_fields = [
        'key',
        'created_at',
        'updated_at',
        'last_used_at',
        'key_details_display'
    ]
    
    # Register actions
    actions = ['activate_selected_keys', 'deactivate_selected_keys', 'regenerate_selected_keys']
    
    # Display methods using utilities
    @display(description="API Key")
    def key_display(self, obj):
        """Masked API key display for security with key icon."""
        if not obj.key:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.KEY_OFF)
            return StatusBadge.create(text="No Key", variant="secondary", config=config)
        
        # Show first 8 and last 4 characters
        masked_key = f"{obj.key[:8]}...{obj.key[-4:]}"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.KEY)
        return StatusBadge.create(
            text=masked_key,
            variant="info",
            config=config
        )
    
    @display(description="User", header=True)
    def user_display(self, obj):
        """User display with avatar."""
        return self.display_user_with_avatar(obj, 'user')
    
    @display(description="Name")
    def name_display(self, obj):
        """API key name display."""
        if not obj.name:
            return StatusBadge.create(text="Unnamed", variant="secondary")
        
        return StatusBadge.create(
            text=obj.name,
            variant="primary"
        )
    
    @display(description="Status", label=True)
    def status_display(self, obj):
        """Status display with activity level."""
        if not obj.is_active:
            return self.display_status_auto(
                type('obj', (), {'status': 'Inactive'})(),
                'status',
                StatusBadgeConfig(custom_mappings={'Inactive': 'danger'})
            )
        
        # Determine activity level based on last usage
        if not obj.last_used_at:
            status = "Active (Unused)"
            variant = "info"
        else:
            days_since_use = (timezone.now() - obj.last_used_at).days
            
            if days_since_use <= 1:
                status = "Active (Recent)"
                variant = "success"
            elif days_since_use <= 7:
                status = "Active (This Week)"
                variant = "success"
            elif days_since_use <= 30:
                status = "Active (This Month)"
                variant = "warning"
            else:
                status = "Active (Idle)"
                variant = "secondary"
        
        config = StatusBadgeConfig(
            custom_mappings={status: variant},
            show_icons=True
        )
        
        return self.display_status_auto(
            type('obj', (), {'status': status})(),
            'status',
            config
        )
    
    @display(description="Usage")
    def usage_display(self, obj):
        """Usage count display."""
        # This would need actual usage tracking implementation
        usage_count = getattr(obj, 'usage_count', 0)
        
        return self.display_count_simple(
            type('obj', (), {'usage_count': usage_count})(),
            'usage_count',
            'requests',
            CounterBadgeConfig(use_humanize=True)
        )
    
    @display(description="Created")
    def created_display(self, obj):
        """Created time display."""
        return self.display_datetime_relative(
            obj,
            'created_at',
            DateTimeDisplayConfig(show_relative=True, show_seconds=False)
        )
    
    # Readonly field displays
    def key_details_display(self, obj):
        """Detailed API key information for detail view."""
        if not obj.pk:
            return "Save to see details"
        
        from django.utils.html import format_html
        from django_cfg.modules.django_admin.utils.displays import DateTimeDisplay
        
        details = []
        
        # Full key (be careful in production!)
        details.append(f"<strong>Full Key:</strong> <code>{obj.key}</code>")
        
        # Usage statistics
        if obj.last_used_at:
            last_used_html = DateTimeDisplay.relative(
                obj.last_used_at,
                DateTimeDisplayConfig(show_relative=True)
            )
            details.append(f"<strong>Last Used:</strong> {last_used_html}")
        else:
            details.append("<strong>Last Used:</strong> Never")
        
        # Age calculation
        age = timezone.now() - obj.created_at
        age_text = f"{age.days} days old"
        details.append(f"<strong>Age:</strong> {age_text}")
        
        # Security info
        if obj.is_active:
            security_status = '<span class="text-green-600">🔓 Active</span>'
        else:
            security_status = '<span class="text-red-600">🔒 Inactive</span>'
        
        details.append(f"<strong>Security Status:</strong> {security_status}")
        
        return format_html("<br>".join(details))
    
    key_details_display.short_description = "Key Details"
    
    # Actions
    @action(description="Activate selected keys", variant=ActionVariant.SUCCESS)
    def activate_keys(self, request, queryset):
        """Activate selected API keys."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Successfully activated {updated} API key(s).",
            level='SUCCESS'
        )
    
    @action(description="Deactivate selected keys", variant=ActionVariant.WARNING)
    def deactivate_keys(self, request, queryset):
        """Deactivate selected API keys."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {updated} API key(s).",
            level='WARNING'
        )
    
    @action(description="Regenerate selected keys", variant=ActionVariant.DANGER)
    def regenerate_keys(self, request, queryset):
        """Regenerate selected API keys."""
        import secrets
        import string
        
        updated_count = 0
        for api_key in queryset:
            # Generate new key
            alphabet = string.ascii_letters + string.digits
            new_key = ''.join(secrets.choice(alphabet) for _ in range(32))
            
            api_key.key = new_key
            api_key.save()
            updated_count += 1
        
        self.message_user(
            request,
            f"Successfully regenerated {updated_count} API key(s).",
            level='WARNING'
        )
