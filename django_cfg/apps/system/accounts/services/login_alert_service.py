"""
Login Alert Service — Apple-style login notification emails.

Sends an email when a user logs in from a new device/IP, so they can
detect unauthorized access. Suppresses noise with smart rules:

- No alert on first login after registration (grace period)
- No alert if same IP + same browser within 24h
- No alert for test accounts
- Background sending (never blocks the auth response)
"""

from __future__ import annotations

import hashlib
import logging
import threading
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from django.utils import timezone

if TYPE_CHECKING:
    from django.http import HttpRequest

    from ..models import CustomUser

logger = logging.getLogger(__name__)

# Grace period after registration — no login alerts
_REGISTRATION_GRACE_HOURS = 24

# Dedup window — same IP + browser fingerprint = no repeat alert
_DEDUP_HOURS = 24


@dataclass(frozen=True, slots=True)
class LoginContext:
    """Parsed login metadata for email template and dedup."""

    ip_address: str
    user_agent: str
    browser: str
    os: str
    device_type: str
    login_time: str  # formatted for display
    fingerprint: str  # hash of ip + browser + os for dedup


def _build_login_context(request: HttpRequest) -> LoginContext:
    """Extract and parse login metadata from the request."""
    from django_cfg.modules.django_monitor.utils import parse_user_agent

    ip = _get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")
    browser, os_name, device_type = parse_user_agent(ua)

    # Fingerprint = hash(ip + browser + os) — same combo within dedup window = skip
    raw = f"{ip}:{browser}:{os_name}"
    fingerprint = hashlib.sha256(raw.encode()).hexdigest()[:16]

    now = timezone.now()
    login_time = now.strftime("%B %d, %Y at %H:%M UTC")

    return LoginContext(
        ip_address=ip,
        user_agent=ua,
        browser=browser or "Unknown browser",
        os=os_name or "Unknown OS",
        device_type=device_type or "desktop",
        login_time=login_time,
        fingerprint=fingerprint,
    )


def _get_client_ip(request: HttpRequest) -> str:
    """Get client IP from request, handling proxies."""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "Unknown")


def _is_within_grace_period(user: CustomUser) -> bool:
    """Check if user registered recently (no login alerts yet)."""
    if not user.date_joined:
        return False
    grace_end = user.date_joined + timedelta(hours=_REGISTRATION_GRACE_HOURS)
    return timezone.now() < grace_end


def _was_recently_seen(user: CustomUser, fingerprint: str) -> bool:
    """Check if this IP+browser combo logged in recently."""
    from ..models import UserActivity
    from ..models.choices import ActivityType

    cutoff = timezone.now() - timedelta(hours=_DEDUP_HOURS)
    return UserActivity.objects.filter(
        user=user,
        activity_type=ActivityType.LOGIN,
        description__contains=fingerprint,
        created_at__gte=cutoff,
    ).exists()


def _send_alert_email(user: CustomUser, ctx: LoginContext) -> None:
    """Send the login alert email (runs in background thread)."""
    from django_cfg.core.state import get_current_config
    from django_cfg.modules.django_email import DjangoEmailService

    config = get_current_config()
    project_name = config.project_name if config else "App"
    site_url = config.site_url if config else ""

    device_label = f"{ctx.browser} on {ctx.os}"
    if ctx.device_type in ("mobile", "tablet"):
        device_label = f"{ctx.browser} on {ctx.os} ({ctx.device_type})"

    subject = f"New sign-in to your {project_name} account"
    logger.info("Login alert email sending to %s (%s, IP %s)", user.email, device_label, ctx.ip_address)

    email_service = DjangoEmailService()
    email_service.send_template(
        subject=subject,
        template_name="emails/login_alert_email",
        context={
            "user": user,
            "device": device_label,
            "ip_address": ctx.ip_address,
            "login_time": ctx.login_time,
            "project_name": project_name,
            "button_url": site_url or "",
        },
        recipient_list=[user.email],
    )
    logger.info("Login alert email sent to %s", user.email)


def _log_activity(user: CustomUser, ctx: LoginContext) -> None:
    """Log login activity with fingerprint in description for dedup."""
    from .activity_service import ActivityService
    from ..models.choices import ActivityType

    ActivityService.log_activity(
        user=user,
        activity_type=ActivityType.LOGIN,
        description=f"Login from {ctx.browser} on {ctx.os} [fp:{ctx.fingerprint}]",
        ip_address=ctx.ip_address,
        user_agent=ctx.user_agent,
        object_type="",
    )


def _do_login_alert(user: CustomUser, ctx: LoginContext) -> None:
    """Execute login alert logic outside the request transaction.

    This runs via transaction.on_commit() so DB writes here cannot
    break the auth response's atomic block.
    """
    try:
        # --- Suppression rules (check BEFORE logging activity) ---

        should_send = True

        # 1. Test accounts — never email
        if getattr(user, "is_test_account", False):
            should_send = False

        # 2. Grace period after registration
        elif _is_within_grace_period(user):
            logger.debug("Login alert suppressed: registration grace period for %s", user.email)
            should_send = False

        # 3. Same IP + browser recently — already alerted
        elif _was_recently_seen(user, ctx.fingerprint):
            logger.debug("Login alert suppressed: recent same-device login for %s", user.email)
            should_send = False

        # Always log activity (after dedup check, so the check sees previous logins)
        _log_activity(user, ctx)

        if not should_send:
            return

        # --- Send email in background thread ---
        thread = threading.Thread(
            target=_send_alert_email,
            args=(user, ctx),
            daemon=True,
            name=f"login-alert-{user.pk}",
        )
        thread.start()

    except Exception:
        logger.exception("Failed to process login alert for %s", getattr(user, "email", "?"))


def send_login_alert(user: CustomUser, request: HttpRequest) -> None:
    """
    Main entry point — call after issuing JWT tokens.

    Defers all work to transaction.on_commit() so DB writes (activity log)
    never break the auth view's atomic block. If no transaction is active,
    runs immediately.
    """
    from django.db import connection, transaction

    try:
        ctx = _build_login_context(request)

        if connection.in_atomic_block:
            transaction.on_commit(lambda: _do_login_alert(user, ctx))
        else:
            _do_login_alert(user, ctx)

    except Exception:
        # Never break authentication flow
        logger.exception("Failed to process login alert for %s", getattr(user, "email", "?"))


__all__ = ["send_login_alert", "LoginContext"]
