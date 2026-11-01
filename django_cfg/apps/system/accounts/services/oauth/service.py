"""The one OAuth flow for every provider: start, consume state, complete, link or create.

Linking rule (one rule, every provider; ``dev/google-oauth/README.md`` decision 6).
After a verified provider email is in hand:

1. ``OAuthConnection(provider, sub)`` exists: that user signs in, whatever the
   provider's email is now.
2. Else the user whose mailbox is the email (``email_key``, not soft-deleted):
   active, not staff: link, whatever ``is_email_verified`` says. An account that
   was never verified also loses its password (a password set before the email
   was proven must not survive the proof).
3. Staff and superusers are never linked by email: ``link_not_allowed``.
4. Nobody: create a verified user.

One verified email is one user, so there is no "unverified account" refusal.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Tuple
from urllib.parse import urlencode

from django.db import IntegrityError, router, transaction
from django.utils import timezone

from django_cfg.modules.django_telegram import DjangoTelegram

from ...models import CustomUser
from ...models.oauth import OAuthConnection, OAuthState
from .base import OAuthError, OAuthErrorCode, OAuthIdentity, OAuthProvider, TokenSet

logger = logging.getLogger(__name__)

# Bound on the opportunistic purge at the start of every flow (the scheduled job removes the rest).
PURGE_BATCH = 500


@dataclass(frozen=True)
class LoginResult:
    """Who signed in. ``email_verified`` is True only when the provider vouched for a real address."""

    user: CustomUser
    user_created: bool
    connection_created: bool
    email_verified: bool


def pkce_challenge(verifier: str) -> str:
    """S256 code challenge of ``verifier`` (RFC 7636)."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


class OAuthService:
    # ------------------------------------------------------------------ start

    @classmethod
    def start(cls, provider: OAuthProvider, *, redirect_uri: str, source_url: str = "") -> Tuple[str, str]:
        """Create the attempt's state row; return ``(authorization_url, state)``."""
        if not provider.is_enabled():
            raise OAuthError(provider.disabled_code)
        cls.purge_expired(limit=PURGE_BATCH)

        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(48) if provider.uses_pkce else ""
        nonce = secrets.token_urlsafe(24) if provider.uses_nonce else ""
        OAuthState.objects.create(
            state=state,
            provider=provider.id,
            redirect_uri=redirect_uri,
            source_url=source_url,
            code_verifier=verifier,
            nonce=nonce,
            expires_at=timezone.now() + timedelta(seconds=provider.state_ttl_seconds),
        )
        params = provider.build_authorize_params(
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=pkce_challenge(verifier) if verifier else "",
            nonce=nonce,
        )
        logger.info("OAuth %s started, state %s...", provider.id, state[:8])
        return f"{provider.authorize_url}?{urlencode(params)}", state

    # ------------------------------------------------------------------ state

    @staticmethod
    def consume_state(state: str, provider_id: str) -> OAuthState:
        """Burn the state and return its row. Raises ``invalid_state``.

        The DELETE is the lock: of two parallel callbacks with the same state
        exactly one deletes the row and proceeds. It runs before every other
        check, so any failure afterwards (wrong provider, expired, bad code)
        still spent the state and a retry starts a new flow.
        """
        db = router.db_for_write(OAuthState)
        row = OAuthState.objects.using(db).filter(pk=state).first()
        if row is None:
            raise OAuthError(OAuthErrorCode.INVALID_STATE)
        # One SQL DELETE whatever delete signals exist, so the row count is the number of rows this call removed.
        removed = OAuthState.objects.using(db).filter(pk=state)._raw_delete(db)
        if removed != 1:
            raise OAuthError(OAuthErrorCode.INVALID_STATE)
        if row.provider != provider_id or row.is_expired:
            logger.warning("OAuth state rejected (provider=%s, expired=%s)", row.provider, row.is_expired)
            raise OAuthError(OAuthErrorCode.INVALID_STATE)
        return row

    @staticmethod
    def purge_expired(limit: int = 0) -> int:
        """Delete expired states (at most ``limit`` when set). Returns how many."""
        expired = OAuthState.objects.filter(expires_at__lte=timezone.now())
        if limit:
            keys = list(expired.values_list("pk", flat=True)[:limit])
            expired = OAuthState.objects.filter(pk__in=keys)
        deleted, _ = expired.delete()
        return deleted

    # --------------------------------------------------------------- complete

    @classmethod
    def complete(cls, provider: OAuthProvider, *, code: str, state: str) -> LoginResult:
        """Callback steps 4-10. Raises ``OAuthError``; the caller does the 2FA branch and token issue."""
        row = cls.consume_state(state, provider.id)
        tokens = provider.exchange_code(
            code=code, redirect_uri=row.redirect_uri, code_verifier=row.code_verifier
        )
        identity = provider.fetch_identity(tokens, nonce=row.nonce)

        if identity.email:
            if not identity.email_verified:
                raise OAuthError(OAuthErrorCode.EMAIL_NOT_VERIFIED)
        elif not provider.allows_placeholder_email:
            raise OAuthError(OAuthErrorCode.EMAIL_MISSING)
        provider.check_policy(identity)

        result = cls.link_or_create(provider, identity, tokens, source_url=row.source_url)
        cls._notify(provider, result, identity)
        return result

    # ----------------------------------------------------------- link / create

    @classmethod
    def link_or_create(
        cls, provider: OAuthProvider, identity: OAuthIdentity, tokens: TokenSet, *, source_url: str = ""
    ) -> LoginResult:
        """The linking rule, in one transaction. A lost race (unique violation) re-reads once."""
        for attempt in (1, 2):
            try:
                with transaction.atomic():
                    return cls._link_or_create(provider, identity, tokens, source_url)
            except IntegrityError:
                if attempt == 2:
                    raise
                logger.info("OAuth %s: concurrent sign-in for the same identity, re-reading", provider.id)
        raise AssertionError("unreachable")  # pragma: no cover

    @classmethod
    def _link_or_create(cls, provider, identity, tokens, source_url) -> LoginResult:
        users = CustomUser.objects
        email = users.clean_email(identity.email)
        verified = bool(email and identity.email_verified)

        # 1. The provider account is already connected: sign that user in.
        connection = (
            OAuthConnection.objects.select_for_update()
            .select_related("user")
            .filter(provider=provider.id, provider_user_id=identity.provider_user_id)
            .first()
        )
        if connection is not None and connection.user.deleted_at is not None:
            # The account was deleted (anonymised). Free the provider identity for a fresh account.
            connection.delete()
            connection = None
        if connection is not None:
            if not connection.user.is_active:
                raise OAuthError(OAuthErrorCode.ACCOUNT_INACTIVE)
            cls._refresh_connection(connection, identity, tokens)
            return LoginResult(connection.user, False, False, verified)

        # 2. A user owns this mailbox: link to it.
        user = users.by_email(email) if email else None
        user_created = False
        if user is not None:
            if not user.is_active:
                raise OAuthError(OAuthErrorCode.ACCOUNT_INACTIVE)
            if user.is_staff or user.is_superuser:
                raise OAuthError(OAuthErrorCode.LINK_NOT_ALLOWED)
            if not user.is_email_verified:
                # A password set before the email was ever proven must not survive the proof.
                user.set_unusable_password()
                user.save(update_fields=["password"])
            logger.info("OAuth %s: linking to existing user %s", provider.id, user.pk)
        else:
            # 3. Nobody: create.
            user = cls._create_user(provider, identity, email, verified, source_url)
            user_created = True

        OAuthConnection.objects.create(
            user=user,
            provider=provider.id,
            provider_user_id=identity.provider_user_id,
            provider_email=email,
            provider_username=identity.username[:100],
            provider_avatar_url=identity.avatar_url[:500],
            provider_name=identity.name[:200],
            access_token=tokens.access_token,
            scopes=tokens.scopes,
            raw_data=identity.raw,
        )
        return LoginResult(user, user_created, True, verified)

    @staticmethod
    def _create_user(
        provider: OAuthProvider, identity: OAuthIdentity, email: str, verified: bool, source_url: str
    ) -> CustomUser:
        username = CustomUser.objects.clean_username(identity.username)
        user, _ = CustomUser.objects.register_user(
            # Only reachable for a provider that allows a placeholder (GitHub with no verified email).
            email=email or f"{username or identity.provider_user_id}@{provider.placeholder_domain}",
            source_url=source_url,
        )
        if identity.name:
            first, _, last = identity.name.partition(" ")
            user.first_name = CustomUser.objects.clean_name(first)
            user.last_name = CustomUser.objects.clean_name(last)
        if username and (not user.username or user.username.startswith("user_")):
            user.username = username
        if verified and not user.is_email_verified:
            user.is_email_verified = True
            user.email_verified_at = timezone.now()
        user.save()
        return user

    @staticmethod
    def _refresh_connection(connection: OAuthConnection, identity: OAuthIdentity, tokens: TokenSet) -> None:
        connection.provider_email = CustomUser.objects.clean_email(identity.email)
        connection.provider_username = identity.username[:100]
        connection.provider_avatar_url = identity.avatar_url[:500]
        connection.provider_name = identity.name[:200]
        connection.access_token = tokens.access_token
        connection.scopes = tokens.scopes
        connection.raw_data = identity.raw
        connection.last_login_at = timezone.now()
        connection.save()

    # ----------------------------------------------------------------- notice

    @staticmethod
    def _notify(provider: OAuthProvider, result: LoginResult, identity: OAuthIdentity) -> None:
        try:
            data = {
                "Email": result.user.email,
                "Provider": provider.name,
                "Username": identity.username or "N/A",
                "User Type": "New User" if result.user_created else "Existing User",
                "Login Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
            if result.user_created:
                DjangoTelegram.send_success(f"New User via {provider.name} OAuth", data)
            else:
                DjangoTelegram.send_info(f"{provider.name} OAuth Login", data)
        except Exception as exc:  # noqa: BLE001 - a notice never blocks a sign-in
            logger.warning("OAuth Telegram notice failed: %s", exc)
