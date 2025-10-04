"""
Twilio Response admin interface using Django Admin Utilities.

Enhanced Twilio response management with Material Icons and optimized queries.
"""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from django_cfg import ExportMixin, ExportForm

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    MoneyDisplayConfig,
    DateTimeDisplayConfig,
    StatusBadgeConfig,
    Icons,
    display
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import TwilioResponse
from .filters import TwilioResponseStatusFilter, TwilioResponseTypeFilter
from .resources import TwilioResponseResource


class TwilioResponseInline(admin.TabularInline):
    """Inline for showing Twilio responses in related models."""
    model = TwilioResponse
    extra = 0
    readonly_fields = ['created_at', 'status', 'message_sid', 'error_code']
    fields = ['response_type', 'service_type', 'status', 'message_sid', 'error_code', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False



@admin.register(TwilioResponse)
class TwilioResponseAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Enhanced Twilio Response admin using Django Admin Utilities."""
    
    # Export configuration
    resource_class = TwilioResponseResource
    export_form_class = ExportForm
    
    # Performance optimization
    select_related_fields = ['otp_secret']
    
    list_display = [
        'identifier_display',
        'service_type_display',
        'response_type_display',
        'status_display',
        'recipient_display',
        'price_display',
        'created_display',
        'error_status_display'
    ]
    list_display_links = ['identifier_display']
    list_filter = [
        TwilioResponseStatusFilter,
        TwilioResponseTypeFilter,
        'service_type',
        'response_type',
        'created_at',
    ]
    search_fields = [
        'message_sid',
        'verification_sid',
        'to_number',
        'error_message',
        'otp_secret__recipient'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'twilio_created_at',
        'response_data_display',
        'request_data_display'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (
            'Basic Information',
            {
                'fields': (
                    'response_type',
                    'service_type',
                    'status',
                    'otp_secret'
                ),
            },
        ),
        (
            'Twilio Identifiers',
            {
                'fields': (
                    'message_sid',
                    'verification_sid',
                ),
            },
        ),
        (
            'Recipients',
            {
                'fields': (
                    'to_number',
                    'from_number',
                ),
            },
        ),
        (
            'Error Information',
            {
                'fields': (
                    'error_code',
                    'error_message',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Pricing',
            {
                'fields': (
                    'price',
                    'price_unit',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Request/Response Data',
            {
                'fields': (
                    'request_data_display',
                    'response_data_display',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Timestamps',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                    'twilio_created_at',
                ),
                'classes': ('collapse',),
            },
        ),
    )
    
    @display(description="Identifier")
    def identifier_display(self, obj):
        """Main identifier display with appropriate icon."""
        identifier = obj.message_sid or obj.verification_sid
        if not identifier:
            return "—"
        
        # Truncate long identifiers
        if len(identifier) > 20:
            identifier = f"{identifier[:17]}..."
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.FINGERPRINT)
        return StatusBadge.create(
            text=identifier,
            variant="info",
            config=config
        )
    
    @display(description="Service")
    def service_type_display(self, obj):
        """Service type display with appropriate icon."""
        service_icons = {
            'sms': Icons.SMS,
            'voice': Icons.PHONE,
            'verify': Icons.VERIFIED,
            'email': Icons.EMAIL,
        }
        
        icon = service_icons.get(obj.service_type, Icons.CLOUD)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_service_type_display(),
            variant="primary",
            config=config
        )
    
    @display(description="Type")
    def response_type_display(self, obj):
        """Response type display with appropriate icon."""
        type_icons = {
            'send': Icons.SEND,
            'verify': Icons.VERIFIED,
            'check': Icons.CHECK_CIRCLE,
        }
        
        icon = type_icons.get(obj.response_type, Icons.DESCRIPTION)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_response_type_display(),
            variant="info",
            config=config
        )
    
    @display(description="Status", label=True)
    def status_display(self, obj):
        """Enhanced status display with appropriate colors and icons."""
        if obj.has_error:
            status = obj.status or 'Error'
            icon = Icons.ERROR
            variant = "danger"
        elif obj.is_successful:
            status = obj.status or 'Success'
            icon = Icons.CHECK_CIRCLE
            variant = "success"
        else:
            status = obj.status or 'Pending'
            icon = Icons.SCHEDULE
            variant = "warning"
        
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
    
    @display(description="Recipient")
    def recipient_display(self, obj):
        """Recipient display with privacy masking."""
        if not obj.to_number:
            return "—"
        
        # Mask phone numbers and emails for privacy
        recipient = obj.to_number
        if '@' in recipient:
            # Email masking
            local, domain = recipient.split('@', 1)
            masked_local = local[:2] + '*' * (len(local) - 2) if len(local) > 2 else local
            masked_recipient = f"{masked_local}@{domain}"
            icon = Icons.EMAIL
        else:
            # Phone masking
            masked_recipient = f"***{recipient[-4:]}" if len(recipient) > 4 else "***"
            icon = Icons.PHONE
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=masked_recipient,
            variant="secondary",
            config=config
        )
    
    @display(description="Price")
    def price_display(self, obj):
        """Price display with currency formatting."""
        if not obj.price or not obj.price_unit:
            return "—"
        
        config = MoneyDisplayConfig(
            currency=obj.price_unit.upper(),
            decimal_places=4,
            show_sign=False
        )
        
        return self.display_money_amount(
            type('obj', (), {'price': obj.price})(),
            'price',
            config
        )
    
    @display(description="Created")
    def created_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @display(description="Error")
    def error_status_display(self, obj):
        """Error status indicator."""
        if obj.has_error:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.ERROR)
            return StatusBadge.create(text="Error", variant="danger", config=config)
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
        return StatusBadge.create(text="OK", variant="success", config=config)
    
    def request_data_display(self, obj):
        """Display formatted request data."""
        if not obj.request_data:
            return "—"
        
        import json
        try:
            formatted = json.dumps(obj.request_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="font-size: 12px; max-height: 300px; overflow-y: auto;">{}</pre>', formatted)
        except (TypeError, ValueError):
            return str(obj.request_data)
    
    request_data_display.short_description = 'Request Data'
    
    def response_data_display(self, obj):
        """Display formatted response data."""
        if not obj.response_data:
            return "—"
        
        import json
        try:
            formatted = json.dumps(obj.response_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="font-size: 12px; max-height: 300px; overflow-y: auto;">{}</pre>', formatted)
        except (TypeError, ValueError):
            return str(obj.response_data)
    
    response_data_display.short_description = 'Response Data'
