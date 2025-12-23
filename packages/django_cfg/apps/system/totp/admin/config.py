"""Admin configuration for TOTP models."""

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    ShortUUIDField,
)

from ..models import BackupCode, TOTPDevice, TwoFactorSession

# TOTP Device Admin Config
totpdevice_config = AdminConfig(
    model=TOTPDevice,
    list_display=["id", "user_email", "name", "status_badge", "is_primary", "confirmed_at", "last_used_at", "failed_attempts"],
    list_filter=["status", "is_primary", "created_at"],
    search_fields=["user__email", "user__username", "name"],
    readonly_fields=["id", "user", "secret_display", "created_at", "confirmed_at", "last_used_at", "last_verified_code"],
    fieldsets=[
        FieldsetConfig(
            title="Device Info",
            fields=["id", "user", "name", "status", "is_primary"],
        ),
        FieldsetConfig(
            title="TOTP Configuration",
            fields=["secret_display"],
        ),
        FieldsetConfig(
            title="Usage Stats",
            fields=["created_at", "confirmed_at", "last_used_at", "failed_attempts", "last_verified_code"],
        ),
    ],
    display_fields=[
        ShortUUIDField(name="id", title="ID", length=8),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "active": "success",
                "disabled": "danger",
            },
        ),
        DateTimeField(name="confirmed_at", title="Confirmed"),
        DateTimeField(name="last_used_at", title="Last Used"),
    ],
    actions=[
        ActionConfig(
            name="disable_devices",
            description="Disable selected devices",
            variant="danger",
            icon=Icons.BLOCK,
            handler="django_cfg.apps.system.totp.admin.device_admin.disable_devices",
        ),
        ActionConfig(
            name="enable_devices",
            description="Enable selected devices",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler="django_cfg.apps.system.totp.admin.device_admin.enable_devices",
        ),
    ],
)

# Backup Code Admin Config
backupcode_config = AdminConfig(
    model=BackupCode,
    list_display=["id", "user_email", "is_used", "used_at", "created_at"],
    list_filter=["is_used", "created_at"],
    search_fields=["user__email", "user__username"],
    readonly_fields=["id", "user", "code_hash_display", "is_used", "used_at", "created_at"],
    fieldsets=[
        FieldsetConfig(
            title="Backup Code Info",
            fields=["id", "user", "code_hash_display"],
        ),
        FieldsetConfig(
            title="Usage",
            fields=["is_used", "used_at", "created_at"],
        ),
    ],
    display_fields=[
        ShortUUIDField(name="id", title="ID", length=8),
        DateTimeField(name="used_at", title="Used At"),
        DateTimeField(name="created_at", title="Created"),
    ],
)

# Two Factor Session Admin Config
twofactorsession_config = AdminConfig(
    model=TwoFactorSession,
    list_display=["id", "user_email", "status", "created_at", "expires_at", "verified_at", "attempts", "ip_address"],
    list_filter=["status", "created_at", "expires_at"],
    search_fields=["user__email", "user__username", "ip_address"],
    readonly_fields=["id", "user", "status", "ip_address", "user_agent_display", "created_at", "expires_at", "verified_at", "attempts", "max_attempts"],
    fieldsets=[
        FieldsetConfig(
            title="Session Info",
            fields=["id", "user", "status"],
        ),
        FieldsetConfig(
            title="Request Context",
            fields=["ip_address", "user_agent_display"],
        ),
        FieldsetConfig(
            title="Timing",
            fields=["created_at", "expires_at", "verified_at"],
        ),
        FieldsetConfig(
            title="Security",
            fields=["attempts", "max_attempts"],
        ),
    ],
    display_fields=[
        ShortUUIDField(name="id", title="ID", length=8),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "verified": "success",
                "expired": "secondary",
                "failed": "danger",
            },
        ),
        DateTimeField(name="created_at", title="Created"),
        DateTimeField(name="expires_at", title="Expires"),
        DateTimeField(name="verified_at", title="Verified"),
    ],
    actions=[
        ActionConfig(
            name="cleanup_expired",
            description="Clean up expired sessions",
            variant="warning",
            icon=Icons.DELETE_SWEEP,
            action_type="changelist",
            handler="django_cfg.apps.system.totp.admin.session_admin.cleanup_expired_action",
        ),
    ],
)
