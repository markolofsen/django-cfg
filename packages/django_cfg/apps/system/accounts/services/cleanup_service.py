"""
Cleanup tasks for the accounts app.

Registered as RQ scheduled jobs via DjangoRQConfig._collect_module_schedules().
All tasks are safe to run multiple times (idempotent).
"""

from django.utils import timezone

from django_cfg.utils import get_logger

logger = get_logger(__name__)


def cleanup_expired_otps() -> dict:
    """
    Delete OTPSecret records that have expired or been used.

    Runs every 10 minutes. Prevents accumulation of stale rows in the
    django_cfg_accounts_otpsecret table.

    Returns:
        dict with 'deleted' count.
    """
    from ..models import OTPSecret

    cutoff = timezone.now()

    # Delete expired OTPs (regardless of is_used)
    deleted_expired, _ = OTPSecret.objects.filter(expires_at__lt=cutoff).delete()

    # Delete used OTPs older than 24 hours (belt-and-suspenders)
    from datetime import timedelta
    used_cutoff = timezone.now() - timedelta(hours=24)
    deleted_used, _ = OTPSecret.objects.filter(is_used=True, expires_at__lt=used_cutoff).delete()

    total = deleted_expired + deleted_used
    if total:
        logger.info(f"OTP cleanup: deleted {total} records (expired={deleted_expired}, old_used={deleted_used})")
    return {"deleted": total}


def cleanup_jwt_blacklist() -> dict:
    """
    Flush expired tokens from the simplejwt blacklist.

    Calls Django management command 'flushexpiredtokens'.
    Runs daily. Prevents token_blacklist table from growing unboundedly.

    Returns:
        dict with 'status'.
    """
    try:
        from django.core.management import call_command
        call_command("flushexpiredtokens", verbosity=0)
        logger.info("JWT blacklist flush completed")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"JWT blacklist flush failed: {e}")
        return {"status": "error", "error": str(e)}


def get_rq_schedules() -> list:
    """
    Return RQ schedule configs for accounts cleanup tasks.

    Called by DjangoRQConfig._collect_module_schedules() so that the
    accounts app owns its own schedule definitions rather than having
    them hardcoded in the framework core.

    Returns:
        list of RQScheduleConfig instances.
    """
    from django_cfg.models.django.django_rq import RQScheduleConfig

    return [
        RQScheduleConfig(
            func="django_cfg.apps.system.accounts.services.cleanup_service.cleanup_expired_otps",
            cron="*/10 * * * *",  # Every 10 minutes
            queue="low",
            description="Delete expired/used OTP secrets",
        ),
        RQScheduleConfig(
            func="django_cfg.apps.system.accounts.services.cleanup_service.cleanup_jwt_blacklist",
            cron="0 3 * * *",  # Daily at 03:00 UTC
            queue="low",
            description="Flush expired JWT blacklist tokens",
        ),
    ]
