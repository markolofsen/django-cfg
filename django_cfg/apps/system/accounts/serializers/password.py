"""Password grant — email + password → the same JWT pair every login flow issues.

Why this does NOT use ``django.contrib.auth.authenticate()`` (which is what
stock ``TokenObtainPairSerializer`` calls):

``CustomUser.email`` is not ``unique=True``. Uniqueness is a PARTIAL constraint
(``unique_active_email``, ``condition=Q(deleted_at__isnull=True)``) so that
soft-deleted accounts may keep their email for GDPR archival. ``ModelBackend``
looks the user up with ``get_by_natural_key`` — an unfiltered ``.get()`` on
``email`` — which can match a soft-deleted row or raise
``MultipleObjectsReturned`` once one email exists twice. So the lookup is done
here, explicitly, against ``alive()`` (``is_active=True, deleted_at__isnull=True``).
"""

from __future__ import annotations

from typing import Any

from rest_framework import serializers
from rest_framework_simplejwt.serializers import PasswordField, TokenObtainPairSerializer

from ..models import CustomUser
from .profile import UserSerializer


class PasswordLoginSerializer(TokenObtainPairSerializer):
    """Validate email+password against live accounts only.

    Subclasses SimpleJWT so the field/validation contract stays theirs, but
    replaces ``validate()`` — the token pair itself is minted by the view via
    ``mint_tokens_for_request`` so the DPoP binding and remembered-session
    lifetime match OTP, OAuth and TOTP exactly.
    """

    username_field = CustomUser.USERNAME_FIELD  # "email"

    remember_me = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Keep this browser signed in for 30 days",
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Replace the parent's plain CharField with an email field so the
        # generated schema/client types it correctly.
        self.fields[self.username_field] = serializers.EmailField(write_only=True)
        # allow_blank: a blank password must fail as *authentication* (401,
        # identical to a wrong one), not as field validation (400) — otherwise
        # the shape of the error leaks that the field reached the credential
        # check at all.
        self.fields["password"] = PasswordField(allow_blank=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = CustomUser.objects.clean_email(attrs.get(self.username_field, ""))
        password = attrs.get("password") or ""

        user = CustomUser.objects.alive().filter(email__iexact=email).first()

        if user is None:
            # Burn one hash comparison anyway so a nonexistent email and a wrong
            # password cost the same wall-clock time (no enumeration by timing).
            # This is what Django's own ModelBackend does for the same reason.
            CustomUser().set_password(password)
            raise self.fail_authentication()

        if not user.has_usable_password() or not user.check_password(password):
            raise self.fail_authentication()

        self.user = user
        return {}

    def fail_authentication(self):
        """Uniform failure — never reveals whether the email exists."""
        from rest_framework import exceptions

        return exceptions.AuthenticationFailed(
            self.error_messages["no_active_account"],
            "no_active_account",
        )


class PasswordLoginResponseSerializer(serializers.Serializer):
    """Password-login response.

    Mirrors the OTP verify response so a client can treat every login flow
    identically. ``requires_2fa=True`` carries a session id instead of tokens.
    """

    requires_2fa = serializers.BooleanField(
        default=False,
        help_text="Whether 2FA verification is required",
    )
    session_id = serializers.UUIDField(
        required=False, allow_null=True,
        help_text="2FA session ID (if requires_2fa is True)",
    )
    refresh = serializers.CharField(
        required=False, allow_null=True,
        help_text="JWT refresh token (if requires_2fa is False)",
    )
    access = serializers.CharField(
        required=False, allow_null=True,
        help_text="JWT access token (if requires_2fa is False)",
    )
    user = UserSerializer(
        required=False, allow_null=True,
        help_text="User information (if requires_2fa is False)",
    )
    should_prompt_2fa = serializers.BooleanField(
        required=False,
        help_text="Whether user should be prompted to enable 2FA",
    )
    persistent_session = serializers.BooleanField(
        required=False,
        help_text="Whether this login should persist across browser restarts",
    )


class PasswordLoginErrorSerializer(serializers.Serializer):
    """Typed error response for password login.

    error_code values:
      - invalid_credentials — wrong email/password, inactive or deleted account
      - rate_limited        — IP rate limit hit
      - locked_out          — too many failed attempts for this email
    """

    error = serializers.CharField(help_text="Human-readable error message")
    error_code = serializers.CharField(help_text="Machine-readable error code")
    retry_after = serializers.IntegerField(
        required=False, allow_null=True,
        help_text="Seconds until the caller may retry (throttled responses only)",
    )


__all__ = [
    "PasswordLoginSerializer",
    "PasswordLoginResponseSerializer",
    "PasswordLoginErrorSerializer",
]
