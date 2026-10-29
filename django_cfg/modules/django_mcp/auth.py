"""Credential check shared by every MCP endpoint (JSON-RPC, ``/info/``, agent chat).

Authorisation is mandatory: there is no anonymous profile, so a request either
presents a credential accepted by the profile it arrived on or it is refused.
One function decides, so the endpoints cannot drift apart.

A credential is any of: the profile's ``access_key``, one of its ``extra_keys``,
a key accepted by its ``key_validator`` (a dotted path to
``callable(key: str) -> user | True | None``, for per-user API keys that live in
the project's database), or, on a profile with ``oauth``, an access token issued
by :mod:`django_cfg.modules.django_mcp.oauth`.

It arrives in ``X-MCP-Access-Key`` or as ``Authorization: Bearer``; the second
is what every OAuth client sends, and lets a key work in clients that take only
a bearer (``codex --bearer-token-env-var``).
"""

import logging
import secrets
from typing import Any, Optional

logger = logging.getLogger(__name__)

HEADER = "X-MCP-Access-Key"


def presented_credential(request) -> Optional[str]:
    """The credential on ``request``: the MCP header, else a bearer token."""
    key = request.headers.get(HEADER)
    if key:
        return key
    scheme, _, token = (request.headers.get("Authorization") or "").partition(" ")
    if scheme.lower() == "bearer" and token.strip():
        return token.strip()
    return None


def challenge(request, credentials: Any) -> str:
    """``WWW-Authenticate`` for a 401: OAuth discovery where the profile has it."""
    if getattr(credentials, "oauth", None):
        from .oauth import www_authenticate

        return www_authenticate(request, credentials)
    return 'MCPAccessKey realm="mcp", header="X-MCP-Access-Key"'


def authenticate(presented: Optional[str], credentials: Any) -> Any:
    """Return the caller (a user object) or ``None`` to refuse.

    ``credentials`` is an ``MCPProfile`` (or any object with the same key
    fields). Never raises: a failure here must read as a refusal, not a 500.
    """
    if not presented:
        return None
    try:
        presented = str(presented)
        candidates = [
            (None, credentials.access_key, getattr(credentials, "service_username", None))
        ] + [
            (k.label, k.access_key, k.service_username)
            for k in (getattr(credentials, "extra_keys", None) or [])
        ]
        matched = None
        for label, key, username in candidates:
            # compare_digest on every candidate: timing must not reveal which
            # one matched, nor recover a key byte by byte.
            if key and secrets.compare_digest(presented, str(key)) and matched is None:
                matched = (label, username)
        if matched is not None:
            label, username = matched
            if label:
                logger.info("MCP request authenticated by key %r", label)
            return _service_account(username)

        if getattr(credentials, "oauth", None):
            from .oauth import user_for_access_token

            user = user_for_access_token(presented, credentials)
            if user is not None:
                return user

        validator = getattr(credentials, "key_validator", None)
        if validator:
            from django.utils.module_loading import import_string

            return _as_user(import_string(validator)(presented))
    except Exception:
        logger.exception("MCP access-key authentication failed unexpectedly")
    return None


def _as_user(result: Any) -> Any:
    if not result:
        return None
    if result is True:
        from django.contrib.auth.models import AnonymousUser

        return AnonymousUser()
    # AnonymousUser.is_active is False by design; only a real account can be inactive.
    if getattr(result, "is_authenticated", False) and not result.is_active:
        return None
    return result


def _service_account(username: Optional[str]) -> Any:
    """The account a key acts as; ``AnonymousUser`` (a machine) when unbound.

    A bound account that is missing or inactive is a refusal, never a silent
    downgrade: deactivating the account is how operators revoke the key.
    """
    from django.contrib.auth.models import AnonymousUser

    if not username:
        return AnonymousUser()
    from django.contrib.auth import get_user_model

    model = get_user_model()
    account = model.objects.filter(**{model.USERNAME_FIELD: username}).first()
    if account is None:
        logger.error("MCP service_username=%r is configured but no such user exists; rejecting.", username)
        return None
    if not account.is_active:
        logger.error(
            "MCP service_username=%r is inactive; rejecting. Re-activate the "
            "account or clear service_username.",
            username,
        )
        return None
    return account


def validate_user_api_key(secret: str) -> Any:
    """Default ``key_validator``: a user's own ``UserAPIKey`` (a UUID).

    One indexed lookup on the unique ``key`` column. Returns the active user or
    ``None``; a regenerated key no longer matches, so rotating ends access.
    """
    import uuid

    try:
        key = uuid.UUID(str(secret).strip())
    except (ValueError, AttributeError):
        return None
    try:
        from django_cfg.apps.system.accounts.models import UserAPIKey
    except ImportError:
        return None
    row = UserAPIKey.objects.select_related("user").filter(key=key, user__is_active=True).first()
    return row.user if row else None
