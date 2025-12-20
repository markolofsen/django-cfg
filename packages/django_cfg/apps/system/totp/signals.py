"""Django signals for TOTP 2FA events."""

from django.dispatch import Signal, receiver

from django_cfg.utils import get_logger

# Define signals
two_factor_enabled = Signal()  # providing_args=["user", "device"]
two_factor_disabled = Signal()  # providing_args=["user"]
two_factor_verified = Signal()  # providing_args=["user", "device", "session"]
two_factor_failed = Signal()  # providing_args=["user", "attempts", "ip_address"]
backup_code_used = Signal()  # providing_args=["user", "remaining_count"]

logger = get_logger(__name__)


@receiver(two_factor_enabled)
def handle_2fa_enabled(sender, user, device, **kwargs):
    """Handle 2FA enabled event."""
    logger.info(f"2FA enabled for user {user.email}, device: {device.name}")

    # Send notification
    try:
        from django_cfg.modules.django_telegram import DjangoTelegram

        DjangoTelegram.send_success(
            "2FA Enabled",
            {
                "User": user.email,
                "Device": device.name,
                "Status": device.status,
            },
        )
    except Exception as e:
        logger.error(f"Failed to send 2FA enabled notification: {e}")


@receiver(two_factor_disabled)
def handle_2fa_disabled(sender, user, **kwargs):
    """Handle 2FA disabled event."""
    logger.info(f"2FA disabled for user {user.email}")

    # Send notification
    try:
        from django_cfg.modules.django_telegram import DjangoTelegram

        DjangoTelegram.send_warning(
            "2FA Disabled",
            {
                "User": user.email,
                "Action": "2FA completely disabled",
            },
        )
    except Exception as e:
        logger.error(f"Failed to send 2FA disabled notification: {e}")


@receiver(two_factor_verified)
def handle_2fa_verified(sender, user, device, session, **kwargs):
    """Handle successful 2FA verification."""
    logger.info(f"2FA verified for user {user.email}, device: {device.name}")

    # Log verification for audit
    try:
        from django_cfg.modules.django_telegram import DjangoTelegram

        DjangoTelegram.send_info(
            "2FA Verification Success",
            {
                "User": user.email,
                "Device": device.name,
                "IP Address": session.ip_address or "Unknown",
                "Session ID": str(session.id),
            },
        )
    except Exception as e:
        logger.error(f"Failed to send 2FA verification notification: {e}")


@receiver(two_factor_failed)
def handle_2fa_failed(sender, user, attempts, ip_address, **kwargs):
    """Handle failed 2FA verification attempt."""
    logger.warning(
        f"2FA verification failed for user {user.email}, "
        f"attempts: {attempts}, IP: {ip_address}"
    )

    # Send alert for suspicious activity
    if attempts >= 3:
        try:
            from django_cfg.modules.django_telegram import DjangoTelegram

            DjangoTelegram.send_error(
                "2FA Failed Attempts Alert",
                {
                    "User": user.email,
                    "Failed Attempts": attempts,
                    "IP Address": ip_address or "Unknown",
                    "Warning": "Multiple failed verification attempts detected",
                },
            )
        except Exception as e:
            logger.error(f"Failed to send 2FA failed notification: {e}")


@receiver(backup_code_used)
def handle_backup_code_used(sender, user, remaining_count, **kwargs):
    """Handle backup code usage."""
    logger.info(f"Backup code used for user {user.email}, {remaining_count} codes remaining")

    # Send warning if running low
    if remaining_count <= 3:
        try:
            from django_cfg.modules.django_telegram import DjangoTelegram

            DjangoTelegram.send_warning(
                "Backup Code Low Warning",
                {
                    "User": user.email,
                    "Remaining Codes": remaining_count,
                    "Action Required": "Regenerate backup codes soon",
                },
            )
        except Exception as e:
            logger.error(f"Failed to send backup code warning: {e}")
