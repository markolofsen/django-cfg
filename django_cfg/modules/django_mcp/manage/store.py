"""The storage contract behind the manage endpoints.

Every method is optional. A store that lacks one (or sets it to
``NotImplemented``) makes that endpoint answer 404, so the widget hides the
part instead of failing. Rows are plain dicts shaped like the wire format.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, Tuple

# Problem code -> HTTP status. Unknown codes read as a conflict.
REFUSAL_STATUS = {"invalid": 422, "key_limit": 409, "rate_limited": 429}


class StoreRefusal(Exception):
    """A store declines a request on purpose; the view maps it to problem JSON."""

    def __init__(self, code: str, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status or REFUSAL_STATUS.get(code, 409)


class AccessStore(Protocol):
    """All methods optional; ``user`` is the signed-in Django user.

    Key row:        ``{id, name, prefix, scopes, created_at, last_used_at, expires_at, status}``
    Connection row: ``{id, client_name, scopes, created_at, last_used_at, expires_at, status}``
    ``status`` is ``active | expired | revoked``.
    """

    def list_keys(self, user) -> List[Dict[str, Any]]: ...

    def create_key(self, user, name: str, scopes: List[str], expires_in_days: Optional[int]) -> Tuple[Dict[str, Any], str]:
        """Return ``(row, secret)``. The secret leaves the server only here."""
        ...

    def revoke_key(self, user, pk: int) -> Any:
        """Idempotent; another user's id changes nothing and does not raise."""
        ...

    def list_connections(self, user) -> List[Dict[str, Any]]: ...

    def revoke_connection(self, user, pk: int) -> Any: ...

    def revoke_all(self, user) -> Tuple[int, int]:
        """Return ``(keys revoked, connections revoked)``."""
        ...

    def usage(self, user) -> Dict[str, Any]:
        """``{units_today, cap_day, units_hour, cap_hour, calls_24h_by_tool}``."""
        ...


def supports(store: Any, method: str) -> bool:
    """Whether ``store`` offers ``method`` (present and not ``NotImplemented``)."""
    attr = getattr(store, method, NotImplemented)
    return attr is not NotImplemented and callable(attr)


def load_store(spec: Any = None) -> Any:
    """A store from a dotted path, a class, or an instance; ``None`` = the default store.

    A dotted path may name a ready instance, a class (instantiated without
    arguments) or a zero-argument factory.
    """
    if spec is None:
        from .default_store import DefaultAccessStore

        return DefaultAccessStore()
    if isinstance(spec, str):
        from django.utils.module_loading import import_string

        spec = import_string(spec)
    if isinstance(spec, type):
        return spec()
    if callable(spec) and not any(supports(spec, m) for m in _METHODS):
        return spec()
    return spec


_METHODS = ("list_keys", "create_key", "revoke_key", "list_connections", "revoke_connection", "revoke_all", "usage")
