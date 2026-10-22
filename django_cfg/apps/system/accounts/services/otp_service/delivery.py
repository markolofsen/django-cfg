"""Background delivery of the OTP email and operator notification.

Rendering the letter, logging the send and talking to Telegram do not belong on
the request path: the client only needs the OTP row to exist. Delivery is
scheduled with ``transaction.on_commit`` so a worker can never run before the
row it announces is visible, and it runs on a daemon thread so it works with no
queue configured.
"""

from __future__ import annotations

import threading
from typing import Optional

from django.db import transaction
from django.utils import timezone

from django_cfg.utils import get_logger

logger = get_logger(__name__)


def _run_inline() -> bool:
    """Run synchronously under the test runner (locmem mail backend).

    A thread outliving the test races the runner's rollback.
    """
    try:
        from django_cfg.modules.django_email.service import DjangoEmailService

        return DjangoEmailService._is_running_under_tests()
    except Exception:
        return False


def _notify_operators_failure(email: str, error: Exception) -> None:
    try:
        from django_cfg.modules.django_telegram import DjangoTelegram

        DjangoTelegram.send_warning(
            "OTP delivery failed",
            {"Email": email, "Error": f"{type(error).__name__}: {error}"},
        )
    except Exception as exc:  # pragma: no cover - telegram is best effort
        logger.warning(f"Could not notify operators about OTP delivery failure: {exc}")


def deliver_otp(
    user_id,
    otp_code: str,
    is_new_user: bool,
    source_url: Optional[str],
) -> None:
    """Send the OTP email and the Telegram operator notice. Never raises."""
    from ...models import CustomUser
    from ...utils.notifications import AccountNotifications

    email = ""
    try:
        user = CustomUser.objects.get(pk=user_id)
        email = user.email

        if user.is_test_account:
            logger.info(f"[TEST ACCOUNT] Skipping OTP email for {email}")
        else:
            AccountNotifications.send_otp_notification(
                user=user,
                otp_code=otp_code,
                is_new_user=is_new_user,
                source_url=source_url,
                send_email=True,
                send_telegram=False,
            )

        _notify_operators(user, otp_code, is_new_user, source_url)
    except Exception as exc:
        logger.error(f"OTP delivery failed for {email or user_id}: {exc}", exc_info=True)
        _notify_operators_failure(email or str(user_id), exc)


def _notify_operators(user, otp_code: str, is_new_user: bool, source_url: Optional[str]) -> None:
    try:
        from django_cfg.modules.django_telegram import DjangoTelegram

        data = {
            "Email": user.email,
            "User Type": "New User" if is_new_user else "Existing User",
            "OTP Code": otp_code,
            "Source URL": source_url or "Direct",
            "Timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        if user.is_test_account:
            data["Mode"] = "TEST ACCOUNT (Email skipped)"

        if is_new_user:
            DjangoTelegram.send_success("New User OTP Request", data)
        elif user.is_test_account:
            DjangoTelegram.send_warning("Test Account OTP Request", data)
        else:
            DjangoTelegram.send_info("OTP Login Request", data)
    except ImportError:
        logger.warning("DjangoTelegram not available for OTP notifications")
    except Exception as exc:
        logger.error(f"Failed to send Telegram OTP notification: {exc}")


def dispatch_otp_delivery(
    user_id,
    otp_code: str,
    is_new_user: bool,
    source_url: Optional[str],
) -> None:
    """Schedule delivery to start once the surrounding transaction commits."""

    def _start() -> None:
        args = (user_id, otp_code, is_new_user, source_url)
        if _run_inline():
            deliver_otp(*args)
            return
        threading.Thread(
            target=deliver_otp, args=args, daemon=True, name="django-cfg-otp-delivery"
        ).start()

    transaction.on_commit(_start)
