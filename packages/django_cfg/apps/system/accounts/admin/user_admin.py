"""
User Admin v2.0 - Hybrid Pydantic Approach

Enhanced user management with Material Icons and clean declarative config.
Note: Uses hybrid approach due to BaseUserAdmin requirement and standalone actions.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import redirect
from django.urls import reverse
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    UserField,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
# TODO: Migrate standalone actions to new ActionConfig system
# from django_cfg.modules.django_admin_old import (
#     ActionVariant,
#     StandaloneActionsMixin,
#     standalone_action,
# )

from django_cfg.modules.base import BaseCfgModule

from ..models import CustomUser
from .filters import UserStatusFilter
from .inlines import (
    UserActivityInline,
    UserEmailLogInline,
    UserRegistrationSourceInline,
    UserSupportTicketsInline,
)
from .resources import CustomUserResource


# ===== User Admin =====

customuser_config = AdminConfig(
    model=CustomUser,

    # Performance optimization
    prefetch_related=["groups", "user_permissions"],

    # Import/Export
    import_export_enabled=True,
    resource_class=CustomUserResource,

    # List display
    list_display=[
        "avatar",
        "email",
        "full_name",
        "status",
        "twofa_status",
        "sources_count",
        "activity_count",
        "emails_count",
        "tickets_count",
        "last_login",
        "date_joined"
    ],

    # Display fields with UI widgets
    display_fields=[
        UserField(
            name="avatar",
            title="Avatar",
            header=True
        ),
        BadgeField(
            name="email",
            title="Email",
            variant="info",
            icon=Icons.EMAIL
        ),
        DateTimeField(
            name="last_login",
            title="Last Login",
            ordering="last_login"
        ),
        DateTimeField(
            name="date_joined",
            title="Joined",
            ordering="date_joined"
        ),
    ],

    # Filters and search
    list_filter=[UserStatusFilter, "is_staff", "is_active", "date_joined"],
    search_fields=["email", "first_name", "last_name"],

    # Readonly fields
    readonly_fields=["date_joined", "last_login"],

    # Ordering
    ordering=["-date_joined"],
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, PydanticAdmin):
    """
    User admin using hybrid Pydantic approach.

    Note: Extends BaseUserAdmin for Django user management functionality.
    Uses PydanticAdmin for declarative config (import/export enabled via config).

    Features:
    - Clean declarative config
    - Import/Export functionality (via import_export_enabled in config)
    - Material Icons integration
    - Dynamic inlines based on enabled apps

    TODO: Migrate standalone actions to new ActionConfig system
    """
    config = customuser_config

    # Forms loaded from unfold.forms
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # Fieldsets (required by BaseUserAdmin)
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": ("email", "first_name", "last_name", "avatar"),
            },
        ),
        (
            "Contact Information",
            {
                "fields": ("company", "phone", "position"),
            },
        ),
        (
            "Authentication",
            {
                "fields": ("password",),
                "classes": ("collapse",),
            },
        ),
        (
            "Permissions & Status",
            {
                "fields": (
                    ("is_active", "is_staff", "is_superuser"),
                    ("groups",),
                    ("user_permissions",),
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("last_login", "date_joined"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    def get_inlines(self, request, obj):
        """Get inlines based on enabled apps."""
        inlines = [UserRegistrationSourceInline, UserActivityInline]

        # Add email log inline if newsletter app is enabled
        try:
            base_module = BaseCfgModule()
            if base_module.is_newsletter_enabled():
                inlines.append(UserEmailLogInline)
            if base_module.is_support_enabled():
                inlines.append(UserSupportTicketsInline)
        except Exception:
            pass

        return inlines

    # Custom display methods using decorators
    @computed_field("Avatar")
    def avatar(self, obj):
        """Enhanced avatar display with fallback initials."""
        # Avatar is handled automatically by UserField in display_fields
        # For custom avatar display, we would use self.html methods
        # For now, return the user object and let the UserField handle it
        return obj.get_full_name() or obj.email

    @computed_field("Full Name")
    def full_name(self, obj):
        """Full name display."""
        full_name = obj.__class__.objects.get_full_name(obj)
        if not full_name:
            return self.html.badge("No name", variant="secondary", icon=Icons.PERSON)

        return self.html.badge(full_name, variant="primary", icon=Icons.PERSON)

    @computed_field("Status")
    def status(self, obj):
        """Enhanced status display with appropriate icons and colors."""
        if obj.is_superuser:
            status = "Superuser"
            icon = Icons.ADMIN_PANEL_SETTINGS
            variant = "danger"
        elif obj.is_staff:
            status = "Staff"
            icon = Icons.SETTINGS
            variant = "warning"
        elif obj.is_active:
            status = "Active"
            icon = Icons.CHECK_CIRCLE
            variant = "success"
        else:
            status = "Inactive"
            icon = Icons.CANCEL
            variant = "secondary"

        return self.html.badge(status, variant=variant, icon=icon)

    @computed_field("2FA")
    def twofa_status(self, obj):
        """Display 2FA status with appropriate badge."""
        if obj.has_2fa_enabled:
            return self.html.badge("2FA", variant="success", icon=Icons.VERIFIED_USER)
        elif obj.requires_2fa:
            return self.html.badge("Required", variant="danger", icon=Icons.WARNING)
        return None

    @computed_field("Sources")
    def sources_count(self, obj):
        """Show count of registration sources for user."""
        count = obj.user_registration_sources.count()
        if count == 0:
            return None

        return self.html.badge(
            f"{count} source{'s' if count != 1 else ''}",
            variant="info",
            icon=Icons.SOURCE
        )

    @computed_field("Activities")
    def activity_count(self, obj):
        """Show count of user activities."""
        count = obj.activities.count()
        if count == 0:
            return None

        return self.html.badge(
            f"{count} activit{'ies' if count != 1 else 'y'}",
            variant="info",
            icon=Icons.HISTORY
        )

    @computed_field("Emails")
    def emails_count(self, obj):
        """Show count of emails sent to user (if newsletter app is enabled)."""
        from django.db.utils import ProgrammingError, OperationalError

        try:
            base_module = BaseCfgModule()

            if not base_module.is_newsletter_enabled():
                return None

            from django_cfg.apps.business.newsletter.models import EmailLog
            count = EmailLog.objects.filter(user=obj).count()
            if count == 0:
                return None

            return self.html.badge(
                f"{count} email{'s' if count != 1 else ''}",
                variant="success",
                icon=Icons.EMAIL
            )
        except (ProgrammingError, OperationalError):
            # Table doesn't exist in database
            return None
        except (ImportError, Exception):
            return None

    @computed_field("Tickets")
    def tickets_count(self, obj):
        """Show count of support tickets for user (if support app is enabled)."""
        from django.db.utils import ProgrammingError, OperationalError

        try:
            base_module = BaseCfgModule()

            if not base_module.is_support_enabled():
                return None

            from django_cfg.apps.business.support.models import Ticket
            count = Ticket.objects.filter(user=obj).count()
            if count == 0:
                return None

            return self.html.badge(
                f"{count} ticket{'s' if count != 1 else ''}",
                variant="warning",
                icon=Icons.SUPPORT_AGENT
            )
        except (ProgrammingError, OperationalError):
            # Table doesn't exist in database
            return None
        except (ImportError, Exception):
            return None

    # TODO: Migrate standalone actions to new ActionConfig system
    # Standalone actions (view_user_emails, view_user_tickets, export_user_data)
    # temporarily disabled during migration from django_admin_old
