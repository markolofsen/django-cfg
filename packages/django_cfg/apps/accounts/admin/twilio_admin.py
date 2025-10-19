"""
Twilio Response Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced Twilio response management with Material Icons and clean declarative config.
"""

import json

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    DateTimeField,
    FieldsetConfig,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import TwilioResponse
from .filters import TwilioResponseStatusFilter, TwilioResponseTypeFilter
from .resources import TwilioResponseResource


# ===== Twilio Response Inline =====

class TwilioResponseInline(admin.TabularInline):
    """Inline for showing Twilio responses in related models."""
    model = TwilioResponse
    extra = 0
    readonly_fields = ['created_at', 'status', 'message_sid', 'error_code']
    fields = ['response_type', 'service_type', 'status', 'message_sid', 'error_code', 'created_at']

    def has_add_permission(self, request, obj=None):
        return False


# ===== Twilio Response Admin =====

twilioresponse_config = AdminConfig(
    model=TwilioResponse,

    # Performance optimization
    select_related=["otp_secret"],

    # Import/Export
    import_export_enabled=True,
    resource_class=TwilioResponseResource,

    # List display
    list_display=[
        "identifier",
        "service_type",
        "response_type",
        "status",
        "recipient",
        "price",
        "created_at",
        "error_status"
    ],

    # Display fields with NEW specialized classes
    display_fields=[
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Filters and search
    list_filter=[
        TwilioResponseStatusFilter,
        TwilioResponseTypeFilter,
        "service_type",
        "response_type",
        "created_at",
    ],
    search_fields=[
        "message_sid",
        "verification_sid",
        "to_number",
        "error_message",
        "otp_secret__recipient"
    ],

    # Readonly fields
    readonly_fields=[
        "created_at",
        "updated_at",
        "twilio_created_at",
        "response_data_display",
        "request_data_display"
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["response_type", "service_type", "status", "otp_secret"]
        ),
        FieldsetConfig(
            title="Twilio Identifiers",
            fields=["message_sid", "verification_sid"]
        ),
        FieldsetConfig(
            title="Recipients",
            fields=["to_number", "from_number"]
        ),
        FieldsetConfig(
            title="Error Information",
            fields=["error_code", "error_message"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Pricing",
            fields=["price", "price_unit"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Request/Response Data",
            fields=["request_data_display", "response_data_display"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at", "twilio_created_at"],
            collapsed=True
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(TwilioResponse)
class TwilioResponseAdmin(PydanticAdmin):
    """
    TwilioResponse admin using NEW Pydantic declarative approach.

    Features:
    - Clean declarative config
    - Import/Export functionality
    - Material Icons integration
    - Privacy-aware recipient display
    """
    config = twilioresponse_config

    # Custom display methods using decorators
    @computed_field("Identifier")
    def identifier(self, obj):
        """Main identifier display with appropriate icon."""
        identifier = obj.message_sid or obj.verification_sid
        if not identifier:
            return None

        # Truncate long identifiers
        if len(identifier) > 20:
            identifier = f"{identifier[:17]}..."

        return self.html.badge(identifier, variant="info", icon=Icons.FINGERPRINT)

    @computed_field("Service")
    def service_type(self, obj):
        """Service type display with appropriate icon."""
        service_icons = {
            'sms': Icons.SMS,
            'voice': Icons.PHONE,
            'verify': Icons.VERIFIED,
            'email': Icons.EMAIL,
        }

        icon = service_icons.get(obj.service_type, Icons.CLOUD)

        return self.html.badge(obj.get_service_type_display(), variant="primary", icon=icon)

    @computed_field("Type")
    def response_type(self, obj):
        """Response type display with appropriate icon."""
        type_icons = {
            'send': Icons.SEND,
            'verify': Icons.VERIFIED,
            'check': Icons.CHECK_CIRCLE,
        }

        icon = type_icons.get(obj.response_type, Icons.DESCRIPTION)

        return self.html.badge(obj.get_response_type_display(), variant="info", icon=icon)

    @computed_field("Status")
    def status(self, obj):
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

        return self.html.badge(status, variant=variant, icon=icon)

    @computed_field("Recipient")
    def recipient(self, obj):
        """Recipient display with privacy masking."""
        if not obj.to_number:
            return None

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

        return self.html.badge(masked_recipient, variant="secondary", icon=icon)

    @computed_field("Price")
    def price(self, obj):
        """Price display with currency formatting."""
        if not obj.price or not obj.price_unit:
            return None

        return self.html.badge(f"{obj.price:.4f} {obj.price_unit.upper()}", variant="info", icon=Icons.ATTACH_MONEY)

    @computed_field("Error")
    def error_status(self, obj):
        """Error status indicator."""
        if obj.has_error:
            return self.html.badge("Error", variant="danger", icon=Icons.ERROR)

        return self.html.badge("OK", variant="success", icon=Icons.CHECK_CIRCLE)

    def request_data_display(self, obj):
        """Display formatted request data using self.html."""
        if not obj.request_data:
            return "—"

        try:
            formatted = json.dumps(obj.request_data, indent=2, ensure_ascii=False)
            return f'<pre style="font-size: 12px; max-height: 300px; overflow-y: auto;">{formatted}</pre>'
        except (TypeError, ValueError):
            return str(obj.request_data)

    request_data_display.short_description = 'Request Data'

    def response_data_display(self, obj):
        """Display formatted response data using self.html."""
        if not obj.response_data:
            return "—"

        try:
            formatted = json.dumps(obj.response_data, indent=2, ensure_ascii=False)
            return f'<pre style="font-size: 12px; max-height: 300px; overflow-y: auto;">{formatted}</pre>'
        except (TypeError, ValueError):
            return str(obj.response_data)

    response_data_display.short_description = 'Response Data'
