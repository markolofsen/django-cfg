"""The shared tail of every OAuth login: 2FA hand-off, token issue, signals."""

from __future__ import annotations

import logging
from typing import Any, Dict

from django_cfg.apps.system.totp.services import TOTPService, TwoFactorSessionService
from django_cfg.modules.base import BaseCfgModule

from ..verification import mark_user_verified
from ..welcome import persist_user_language
from .service import LoginResult

logger = logging.getLogger(__name__)


def finalize_login(request, result: LoginResult, *, sender: type) -> Dict[str, Any]:
    """Turn a ``LoginResult`` into the ``OAuthTokenResponse`` body.

    With 2FA enabled system-wide and a TOTP device on the user, no token is
    issued: the body carries a 2FA session id instead.
    """
    user = result.user

    if BaseCfgModule().is_totp_enabled() and TOTPService.has_active_device(user):
        session = TwoFactorSessionService.create_session(user, request)
        logger.info("2FA required for OAuth user %s, session %s", user.pk, session.id)
        return {
            "requires_2fa": True,
            "session_id": str(session.id),
            "access": None,
            "refresh": None,
            "user": None,
            "is_new_user": result.user_created,
            "is_new_connection": result.connection_created,
            "should_prompt_2fa": False,
        }

    # Remembered sessions are capped at 30 days.
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    from ...signals import user_authenticated

    user_authenticated.send(sender=sender, user=user, request=request)

    # Persist the browser's language before announcing verification: the welcome
    # email receiver reads ``user.language``, and there is no OTP request on this
    # path to carry it.
    persist_user_language(user, request.META.get("HTTP_ACCEPT_LANGUAGE", "") or "")

    # Announce a proven email the way the OTP path does (the extension point
    # products use to enroll a newsletter). Only a real, provider-verified
    # address proves anything: a placeholder address does not.
    if result.email_verified:
        mark_user_verified(user)

    return {
        "requires_2fa": False,
        "session_id": None,
        "access": str(access),
        "refresh": str(refresh),
        "user": {
            "id": user.pk,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        "is_new_user": result.user_created,
        "is_new_connection": result.connection_created,
        "should_prompt_2fa": user.should_prompt_2fa,
    }
