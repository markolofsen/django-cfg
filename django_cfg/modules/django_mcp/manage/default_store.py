"""The default store: keys in ``McpKey``, connections in ``McpGrant``.

**OAuth stays stateless.** django-cfg's OAuth signs its tokens with
``SECRET_KEY`` and stores nothing, so nothing ever writes ``McpGrant`` and
there is nothing to list or revoke. Connections are therefore reported as
unsupported (404) unless the project opts in with ``stateful_oauth=True``,
meaning it issues grants itself. Usage is unsupported too: ``MCPAuditLog``
carries no user.

Wire the keys to authentication with ``key_validator`` pointing at
:func:`validate_key`.
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

KEY_PREFIX = "mcp_"
SHOWN_PREFIX = 12
NAME_MAX = 40
MAX_KEYS = 5
DEFAULT_DAYS = 180
MAX_DAYS = 3650
USAGE_TOUCH_S = 300
LIST_LIMIT = 50
_SCOPE_RE = re.compile(r"^[a-z0-9:_.-]{1,32}$")


def new_secret() -> str:
    return KEY_PREFIX + base64.b32encode(os.urandom(25)).decode().rstrip("=")


def digest(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def key_row(row) -> Dict[str, Any]:
    return {
        "id": row.pk, "name": row.name, "prefix": row.prefix, "scopes": list(row.scopes),
        "created_at": row.created_at, "last_used_at": row.last_used_at,
        "expires_at": row.expires_at, "status": row.status,
    }


def validate_key(secret: str):
    """``key_validator`` for the profile: the key's user, or ``None`` to refuse.

    One indexed lookup on the hash. Refuses unknown, revoked and expired keys
    and inactive users. ``last_used_at`` moves at most every five minutes.
    """
    from ..models import McpKey

    if not secret or not secret.startswith(KEY_PREFIX):
        return None
    row = McpKey.objects.select_related("user").filter(key_hash=digest(secret)).first()
    now = timezone.now()
    if row is None or row.revoked_at is not None or row.expires_at <= now or not row.user.is_active:
        return None
    McpKey.objects.filter(pk=row.pk).filter(
        Q(last_used_at__isnull=True) | Q(last_used_at__lte=now - timedelta(seconds=USAGE_TOUCH_S))
    ).update(last_used_at=now)
    return row.user


class DefaultAccessStore:
    """Keys fully; connections only with ``stateful_oauth=True``; no usage."""

    usage = NotImplemented

    def __init__(self, stateful_oauth: bool = False):
        self.stateful_oauth = stateful_oauth
        if not stateful_oauth:
            self.list_connections = NotImplemented
            self.revoke_connection = NotImplemented

    # keys

    def list_keys(self, user) -> List[Dict[str, Any]]:
        from ..models import McpKey

        return [key_row(r) for r in McpKey.objects.filter(user_id=user.pk)[:LIST_LIMIT]]

    def create_key(self, user, name: str, scopes: List[str], expires_in_days: Optional[int]) -> Tuple[Dict[str, Any], str]:
        from django.contrib.auth import get_user_model

        from ..models import McpKey
        from .store import StoreRefusal

        name = " ".join((name or "").split())
        if not 1 <= len(name) <= NAME_MAX:
            raise StoreRefusal("invalid", f"name must be 1 to {NAME_MAX} characters")
        scopes = list(dict.fromkeys(scopes or []))
        bad = [s for s in scopes if not isinstance(s, str) or not _SCOPE_RE.match(s)]
        if bad or len(scopes) > 16:
            raise StoreRefusal("invalid", "scopes must be up to 16 short lowercase names")
        days = DEFAULT_DAYS if expires_in_days is None else expires_in_days
        if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= MAX_DAYS:
            raise StoreRefusal("invalid", f"expires_in_days must be 1 to {MAX_DAYS}")
        now = timezone.now()
        with transaction.atomic():
            # Serialises one user's creations so the limit cannot be raced.
            get_user_model().objects.select_for_update().filter(pk=user.pk).first()
            active = McpKey.objects.filter(user_id=user.pk, revoked_at__isnull=True, expires_at__gt=now).count()
            if active >= MAX_KEYS:
                raise StoreRefusal("key_limit", f"at most {MAX_KEYS} active keys")
            secret = new_secret()
            row = McpKey.objects.create(
                user_id=user.pk, name=name, prefix=secret[:SHOWN_PREFIX], key_hash=digest(secret),
                scopes=scopes, expires_at=now + timedelta(days=days),
            )
        return key_row(row), secret

    def revoke_key(self, user, pk: int) -> bool:
        from ..models import McpKey

        return McpKey.objects.filter(pk=pk, user_id=user.pk, revoked_at__isnull=True).update(revoked_at=timezone.now()) > 0

    # connections (stateful_oauth only)

    def list_connections(self, user) -> List[Dict[str, Any]]:
        from ..models import McpGrant

        return [
            {
                "id": g.pk, "client_name": g.client_name, "scopes": list(g.scopes), "created_at": g.created_at,
                "last_used_at": g.last_used_at, "expires_at": None,
                "status": "revoked" if g.revoked_at else "active",
            }
            for g in McpGrant.objects.filter(user_id=user.pk)[:LIST_LIMIT]
        ]

    def revoke_connection(self, user, pk: int) -> bool:
        from ..models import McpGrant

        return McpGrant.objects.filter(pk=pk, user_id=user.pk, revoked_at__isnull=True).update(revoked_at=timezone.now()) > 0

    def revoke_all(self, user) -> Tuple[int, int]:
        from ..models import McpGrant, McpKey

        now = timezone.now()
        keys = McpKey.objects.filter(user_id=user.pk, revoked_at__isnull=True).update(revoked_at=now)
        grants = 0
        if self.stateful_oauth:
            grants = McpGrant.objects.filter(user_id=user.pk, revoked_at__isnull=True).update(revoked_at=now)
        return keys, grants
