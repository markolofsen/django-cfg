"""
Twilio Response admin configuration.
"""

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from django_cfg import ExportMixin, ExportForm

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
class TwilioResponseAdmin(ModelAdmin, ExportMixin):
    # Export-only configuration
    resource_class = TwilioResponseResource
    export_form_class = ExportForm
    list_display = [
        'identifier', 
        'service_type', 
        'response_type', 
        'status_display', 
        'recipient', 
        'price_display',
        'created_display',
        'has_error_display'
    ]
    list_display_links = ['identifier']
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

    def identifier(self, obj):
        """Get the main identifier for the response."""
        return obj.message_sid or obj.verification_sid or '—'
    identifier.short_description = 'Identifier'

    def status_display(self, obj):
        """Display status with color coding."""
        if obj.has_error:
            return format_html(
                '<span style="color: #dc3545;">❌ {}</span>',
                obj.status or 'Error'
            )
        elif obj.is_successful:
            return format_html(
                '<span style="color: #28a745;">✅ {}</span>',
                obj.status or 'Success'
            )
        else:
            return format_html(
                '<span style="color: #ffc107;">⏳ {}</span>',
                obj.status or 'Unknown'
            )
    status_display.short_description = 'Status'

    def recipient(self, obj):
        """Display recipient with masking for privacy."""
        if not obj.to_number:
            return '—'
        
        # Mask phone numbers and emails for privacy
        recipient = obj.to_number
        if '@' in recipient:
            # Email masking
            local, domain = recipient.split('@', 1)
            masked_local = local[:2] + '*' * (len(local) - 2)
            return f"{masked_local}@{domain}"
        else:
            # Phone masking
            return f"***{recipient[-4:]}" if len(recipient) > 4 else "***"
    recipient.short_description = 'Recipient'

    def price_display(self, obj):
        """Display price with currency."""
        if obj.price and obj.price_unit:
            return f"{obj.price} {obj.price_unit.upper()}"
        return '—'
    price_display.short_description = 'Price'

    def created_display(self, obj):
        """Display created time with natural time."""
        return naturaltime(obj.created_at)
    created_display.short_description = 'Created'

    def has_error_display(self, obj):
        """Display error status."""
        if obj.has_error:
            return format_html('<span style="color: #dc3545;">❌</span>')
        return format_html('<span style="color: #28a745;">✅</span>')
    has_error_display.short_description = 'Error'

    def request_data_display(self, obj):
        """Display formatted request data."""
        if not obj.request_data:
            return '—'
        
        import json
        try:
            formatted = json.dumps(obj.request_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="font-size: 12px;">{}</pre>', formatted)
        except (TypeError, ValueError):
            return str(obj.request_data)
    request_data_display.short_description = 'Request Data'

    def response_data_display(self, obj):
        """Display formatted response data."""
        if not obj.response_data:
            return '—'
        
        import json
        try:
            formatted = json.dumps(obj.response_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="font-size: 12px;">{}</pre>', formatted)
        except (TypeError, ValueError):
            return str(obj.response_data)
    response_data_display.short_description = 'Response Data'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('otp_secret')
