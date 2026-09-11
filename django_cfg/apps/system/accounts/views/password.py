"""Password grant — email + password login.

The human login paths in this framework are email OTP, OAuth and API keys.
This adds the classic password grant for clients that hold a password (CLI
tools, service accounts with a human owner, products that manage their own
credentials).

It deliberately reuses the OTP path's machinery rather than SimpleJWT's
``TokenObtainPairView``:

* tokens come from ``mint_tokens_for_request`` — the ONE mint helper — so the
  pair carries the same ``cnf.jkt`` DPoP binding and the same remembered-session
  deadline as OTP/OAuth/TOTP. Stock ``TokenObtainPairSerializer.get_token``
  calls ``RefreshToken.for_user`` directly and would silently issue unbound
  tokens.
* the 2FA branch is identical, so enabling TOTP does not leave a password
  bypass open.
* the user lookup excludes soft-deleted rows (see serializers/password.py).

Throttling is stricter than OTP verify, because a password is guessable in a
way a one-time code sent to a mailbox is not: 10 attempts/minute per IP (vs 20
for OTP verify) plus a per-email lockout (5 failures → 15 minutes).

**That lockout has its own cache keys** (``PasswordLoginThrottle``). It shared
OTP verify's until 2026-09-11, which meant five wrong password guesses also
locked the account owner out of OTP login — an attacker who could not guess the
password could still deny the route that did not need one. The per-IP limit is
still shared, and that one is deliberate: it counts the attacker, not the
victim.
"""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from django_cfg.apps.system.totp.services import TOTPService, TwoFactorSessionService
from django_cfg.modules.base import BaseCfgModule

from ..serializers.password import (
    PasswordLoginErrorSerializer,
    PasswordLoginResponseSerializer,
    PasswordLoginSerializer,
)
from ..serializers.profile import UserSerializer
from ..services.brute_force_service import PasswordLoginThrottle
from .otp import _is_ip_limited

logger = logging.getLogger(__name__)

# Per-IP attempt budget. Half the OTP-verify allowance — a password is a
# standing secret, an OTP is a 4-digit code that expires in minutes.
PASSWORD_LOGIN_IP_RATE = "10/m"


@extend_schema(
    request=PasswordLoginSerializer,
    responses={
        200: PasswordLoginResponseSerializer,
        401: PasswordLoginErrorSerializer,
        429: PasswordLoginErrorSerializer,
    },
    tags=["cfg_accounts_auth"],
)
class PasswordLoginView(TokenObtainPairView):
    """Obtain a JWT pair with email + password.

    Returns the same envelope as OTP verify: either ``requires_2fa=True`` with
    a session id, or the token pair plus the user object. Failures are uniform
    (401 ``invalid_credentials``) whether the email is unknown, the password is
    wrong, or the account is inactive/soft-deleted — no enumeration.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordLoginSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        if _is_ip_limited(request, group="password_login_ip", rate=PASSWORD_LOGIN_IP_RATE):
            return Response(
                {"error": "Too many requests", "error_code": "rate_limited"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = self.get_serializer(data=request.data)

        # The email is needed for the per-account lockout before credentials are
        # checked, so read it off the raw payload — a malformed one just falls
        # through to the serializer's own validation error.
        from ..models import CustomUser

        email = CustomUser.objects.clean_email(str(request.data.get("email") or ""))
        if email:
            locked, retry_after = PasswordLoginThrottle.is_locked(email)
            if locked:
                logger.warning("Password login blocked - account locked: %s", email)
                return Response(
                    {
                        "error": "Too many failed attempts. Please try again later.",
                        "error_code": "locked_out",
                        "retry_after": retry_after,
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            if email:
                just_locked, _remaining = PasswordLoginThrottle.record_failure(email)
                if just_locked:
                    logger.warning("Password brute-force lockout triggered for %s", email)
            logger.warning("Failed password login for %s", email or "<no email>")
            return Response(
                {"error": "Authentication failed", "error_code": "invalid_credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = serializer.user
        remember_me: bool = serializer.validated_data.get("remember_me", False) or bool(
            request.data.get("remember_me")
        )

        PasswordLoginThrottle.record_success(user.email)

        # 2FA gate — identical to the OTP path, so a password cannot bypass it.
        if BaseCfgModule().is_totp_enabled() and TOTPService.has_active_device(user):
            session = TwoFactorSessionService.create_session(user, request, remember_me=remember_me)
            logger.info("2FA required for password login %s, session %s", user.email, session.id)
            return Response(
                {
                    "requires_2fa": True,
                    "session_id": str(session.id),
                    "refresh": None,
                    "access": None,
                    "user": None,
                    "should_prompt_2fa": False,
                    "persistent_session": remember_me,
                },
                status=status.HTTP_200_OK,
            )

        # Mint via the shared helper — DPoP-bound when a login proof is present.
        from django_cfg.middleware.dpop import REMEMBER_ME_LIFETIME, mint_tokens_for_request

        refresh, access = mint_tokens_for_request(
            user,
            request,
            refresh_lifetime=REMEMBER_ME_LIFETIME if remember_me else None,
        )

        from ..signals import user_authenticated

        user_authenticated.send(sender=self.__class__, user=user, request=request)

        return Response(
            {
                "requires_2fa": False,
                "session_id": None,
                "refresh": str(refresh),
                "access": str(access),
                "user": UserSerializer(user, context={"request": request}).data,
                "should_prompt_2fa": user.should_prompt_2fa,
                "persistent_session": remember_me,
            },
            status=status.HTTP_200_OK,
        )


__all__ = ["PasswordLoginView"]
