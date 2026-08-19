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

# `BaseCfgModule` import removed 2026-08-19: its only two uses here called
# `is_newsletter_enabled()` / `is_support_enabled()`, methods that do not exist.
# Left in place it would read as "this admin consults feature flags", which is
# precisely the impression that kept four dead code paths looking intentional.

from ..models import CustomUser
from .filters import UserStatusFilter
from .inlines import (
    UserActivityInline,
    UserAPIKeyInline,
    UserRegistrationSourceInline,
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
        # "tickets_count" removed 2026-08-19 with the method: no Ticket model
        # exists in django_cfg, so the column could only ever render blank.
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
                BadgeRule(
                    condition_field="is_email_verified",
                    condition_value=True,
                    label="Email verified",
                    variant="success",
                    icon=Icons.MARK_EMAIL_READ,
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
        FilterConfig(field="is_email_verified", type="boolean"),
        FilterConfig(field="date_joined", type="range_date"),
    ],
    search_fields=["email", "first_name", "last_name"],

    # Readonly fields
    readonly_fields=["date_joined", "last_login", "deleted_at", "email_verified_at"],

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
                "fields": ("company", "phone", "position", "language", "timezone"),
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
                    ("is_test_account", "is_email_verified"),
                    ("groups",),
                    ("user_permissions",),
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("last_login", "date_joined", "deleted_at", "email_verified_at"),
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
        """The inlines this admin shows. All three are unconditional.

        **This method used to be conditional, and the condition never ran.** It
        called ``BaseCfgModule().is_newsletter_enabled()``, which does not exist,
        inside a ``try: … except Exception: pass``. So the ``AttributeError``
        aborted the block on its FIRST line — meaning the second check
        (``is_support_enabled``) was unreachable too, and both optional inlines
        were silently dropped for every project. Measured before the fix on
        cmdop's live configuration: three inlines returned, not five.

        Neither of the two could be repaired: their models
        (``business.newsletter.EmailLog``, ``business.support.Ticket``) do not
        exist anywhere in django_cfg, so they were removed along with this
        condition — see the note in ``inlines.py``. Mail history now lives in the
        ``emails_count`` column and ``EmailLogAdmin``.

        Returning a plain list is the point: there is no longer a feature flag to
        get wrong, and adding a genuinely optional inline later should gate on
        ``apps.is_installed(...)``, which fails loudly when its argument is wrong.
        """
        return [UserRegistrationSourceInline, UserActivityInline, UserAPIKeyInline]

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
        """How much mail this person has been sent, from the mailer's own log.

        **This column returned `None` for every user of every project, since it
        was written.** It called ``base_module.is_newsletter_enabled()`` — a method
        that has never existed, ``BaseCfgModule`` defines eight ``is_*_enabled``
        and not that one — and then imported ``django_cfg.apps.business.newsletter``,
        an app that has never existed either. Either alone raises; both were
        caught by ``except (…, Exception)``, which cannot fail. So the panel was
        not "disabled because newsletter is off"; it was broken, and looked
        identical to off.

        Now reads ``django_cfg_mailer.EmailLog``, which is real and populated
        (100 rows on cmdop prod at the time of writing).

        Joined on ``user_id``, not on a relation: ``EmailLog.user_id`` is an
        ``IntegerField`` by design — mail also goes to addresses with no account,
        and a letter's record should outlive the account being deleted — so there
        is no ``user=`` lookup to make. That same absence is why this is a column
        and not a ``TabularInline``: an inline requires a ForeignKey to the parent.

        The narrow ``except`` is deliberate. A missing table (``ProgrammingError``)
        is a project that has not migrated the mailer, and a column must not break
        the user page over it. An ``AttributeError`` from a renamed field is a bug
        and should surface — swallowing everything is what hid this for as long as
        it existed.
        """
        from django.db.utils import OperationalError, ProgrammingError

        try:
            from django_cfg.apps.system.mailer.models import EmailLog
        except ImportError:
            # The mailer app is optional; without it there is no mail to count.
            return None

        try:
            count = EmailLog.objects.filter(user_id=obj.pk).count()
        except (ProgrammingError, OperationalError):
            return None

        if count == 0:
            return None
        return self.html.badge(
            f"{count} email{'s' if count != 1 else ''}",
            variant="success",
            icon=Icons.EMAIL,
        )

    # `tickets_count` was REMOVED here rather than repaired, 2026-08-19.
    #
    # It had the same two defects as `emails_count` above — `is_support_enabled()`
    # is not a method of `BaseCfgModule`, and `django_cfg.apps.business.support`
    # is not an app — but unlike email there is nothing to point it at: **no
    # `Ticket` model exists anywhere in django_cfg** (`rg "class Ticket\b"`
    # returns nothing, and `apps/` holds only api/payments/system/tools; there is
    # no `business` package at all). A column whose data source does not exist
    # cannot be fixed, and leaving it returning `None` behind a blanket `except`
    # is what made four separate dead code paths look like configuration.
    #
    # If a support app is ever added, add the column back then — against the model
    # it actually ships, not against a guessed import path.
