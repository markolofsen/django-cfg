"""
User Admin v2.1 — Declarative Pydantic approach.

Uses StatusBadgesField, FilterConfig (range_date), ActionConfig, StackedField
from django_cfg.modules.django_admin for a clean, code-reduced admin.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    BadgeRule,
    BooleanField,
    DateTimeField,
    FilterConfig,
    Icons,
    RowItem,
    StackedField,
    StatusBadgesField,
    UserField,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

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


# ===== Action handlers =====

def restore_accounts_handler(modeladmin, request, queryset):
    """Restore soft-deleted accounts."""
    restored = 0
    errors = []

    for user in queryset.filter(deleted_at__isnull=False):
        try:
            user.restore()
            restored += 1
        except ValueError:
            errors.append(
                f"{user.email} — email is already taken by an active account. "
                "Open the user record and change the email before restoring."
            )

    if restored:
        modeladmin.message_user(request, f"Successfully restored {restored} account(s).")
    for msg in errors:
        modeladmin.message_user(request, msg, level=messages.ERROR)


def soft_delete_accounts_handler(modeladmin, request, queryset):
    """Soft delete selected accounts (skips superusers)."""
    deleted = 0
    for user in queryset.filter(deleted_at__isnull=True):
        if user.is_superuser:
            continue
        user.soft_delete()
        deleted += 1
    modeladmin.message_user(request, f"Successfully deleted {deleted} account(s).")


# ===== Config =====

customuser_config = AdminConfig(
    model=CustomUser,

    # Performance
    prefetch_related=["groups", "user_permissions"],

    # Import/Export
    import_export_enabled=True,
    resource_class=CustomUserResource,

    # List display
    list_display=[
        "avatar",
        "user_info",
        "account_flags",
        "language",
        "twofa_status",
        "sources_count",
        "activity_count",
        "emails_count",
        "tickets_count",
        "last_login",
        "date_joined",
    ],

    # Declarative display fields
    display_fields=[
        UserField(
            name="avatar",
            title="Avatar",
            header=True,
        ),
        StackedField(
            name="user_info",
            title="User",
            rows=[
                RowItem(field="email", bold=True),
                RowItem(field="full_name", muted=True, hide_if_empty=True),
                RowItem(field="company", muted=True, hide_if_empty=True),
            ],
        ),
        StatusBadgesField(
            name="account_flags",
            title="Status",
            badge_rules=[
                BadgeRule(
                    condition_field="is_deleted",
                    condition_value=True,
                    label="Deleted",
                    variant="danger",
                    icon=Icons.DELETE,
                ),
                BadgeRule(
                    condition_field="is_superuser",
                    condition_value=True,
                    label="Superuser",
                    variant="danger",
                    icon=Icons.ADMIN_PANEL_SETTINGS,
                ),
                BadgeRule(
                    condition_field="is_staff",
                    condition_value=True,
                    label="Staff",
                    variant="warning",
                    icon=Icons.SETTINGS,
                ),
                BadgeRule(
                    condition_field="is_test_account",
                    condition_value=True,
                    label="Test",
                    variant="info",
                    icon=Icons.SCIENCE,
                ),
                BadgeRule(
                    condition_field="is_active",
                    condition_value=True,
                    label="Active",
                    variant="success",
                    icon=Icons.CHECK_CIRCLE,
                ),
                BadgeRule(
                    condition_field="is_active",
                    condition_value=False,
                    label="Inactive",
                    variant="secondary",
                    icon=Icons.CANCEL,
                ),
            ],
        ),
        BooleanField(
            name="is_test_account",
            title="Test",
        ),
        DateTimeField(
            name="last_login",
            title="Last Login",
            ordering="last_login",
            show_relative=True,
        ),
        DateTimeField(
            name="date_joined",
            title="Joined",
            ordering="date_joined",
        ),
    ],

    # Filters — UserStatusFilter covers deleted/active/staff/superuser;
    # FilterConfig with range_date replaces the useless DateHierarchy on date_joined.
    list_filter=[
        UserStatusFilter,
        FilterConfig(field="is_test_account", type="boolean"),
        FilterConfig(field="date_joined", type="range_date"),
    ],
    search_fields=["email", "first_name", "last_name"],

    # Readonly fields
    readonly_fields=["date_joined", "last_login", "deleted_at"],

    # Ordering
    ordering=["-date_joined"],

    # Declarative actions
    actions=[
        ActionConfig(
            name="restore_accounts",
            description="Restore selected deleted accounts",
            action_type="bulk",
            variant="success",
            icon=Icons.RESTORE,
            handler=restore_accounts_handler,
        ),
        ActionConfig(
            name="soft_delete_accounts",
            description="Soft delete selected accounts",
            action_type="bulk",
            variant="danger",
            icon=Icons.DELETE,
            confirmation=True,
            handler=soft_delete_accounts_handler,
        ),
    ],
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, PydanticAdmin):
    """
    User admin — hybrid Pydantic approach.

    Extends BaseUserAdmin for Django user management functionality.
    Uses PydanticAdmin for declarative config (import/export, display fields,
    StatusBadgesField, FilterConfig, ActionConfig).
    """
    config = customuser_config

    # Forms from unfold
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
                "fields": ("company", "phone", "position", "language"),
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
                    ("is_test_account",),
                    ("groups",),
                    ("user_permissions",),
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("last_login", "date_joined", "deleted_at"),
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
        try:
            base_module = BaseCfgModule()
            if base_module.is_newsletter_enabled():
                inlines.append(UserEmailLogInline)
            if base_module.is_support_enabled():
                inlines.append(UserSupportTicketsInline)
        except Exception:
            pass
        return inlines

    # === Computed display methods ===

    @computed_field("Avatar")
    def avatar(self, obj):
        """Handled by UserField — returns user object for display."""
        return obj.get_full_name() or obj.email

    @computed_field("2FA")
    def twofa_status(self, obj):
        """Display 2FA status."""
        if obj.has_2fa_enabled:
            return self.html.badge("2FA", variant="success", icon=Icons.VERIFIED_USER)
        elif obj.requires_2fa:
            return self.html.badge("Required", variant="danger", icon=Icons.WARNING)
        return None

    @computed_field("Sources")
    def sources_count(self, obj):
        """Count of registration sources."""
        count = obj.user_registration_sources.count()
        if count == 0:
            return None
        return self.html.badge(
            f"{count} source{'s' if count != 1 else ''}",
            variant="info",
            icon=Icons.SOURCE,
        )

    @computed_field("Activities")
    def activity_count(self, obj):
        """Count of user activities."""
        count = obj.activities.count()
        if count == 0:
            return None
        return self.html.badge(
            f"{count} activit{'ies' if count != 1 else 'y'}",
            variant="info",
            icon=Icons.HISTORY,
        )

    @computed_field("Emails")
    def emails_count(self, obj):
        """Count of emails (newsletter app)."""
        from django.db.utils import OperationalError, ProgrammingError
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
                icon=Icons.EMAIL,
            )
        except (ProgrammingError, OperationalError, ImportError, Exception):
            return None

    @computed_field("Tickets")
    def tickets_count(self, obj):
        """Count of support tickets."""
        from django.db.utils import OperationalError, ProgrammingError
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
                icon=Icons.SUPPORT_AGENT,
            )
        except (ProgrammingError, OperationalError, ImportError, Exception):
            return None
