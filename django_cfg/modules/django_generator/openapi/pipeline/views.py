"""Name the Django view behind an OpenAPI operation, for generation errors (H2.8).

The spec does not record the view, so the path is resolved through the project's URLconf. Path parameters
(``{id}``) are filled with sample values until one resolves. Without Django, or for a path that does not resolve, the
description falls back to the method and path, which is enough to find the route.
"""

from __future__ import annotations

import re
import uuid

_PARAM = re.compile(r"\{[^}/]+\}")
_SAMPLES = ("1", str(uuid.UUID(int=1)), "x")


def view_for(path: str, method: str) -> str | None:
    """``module.ViewClass`` (``.action`` for a viewset route) serving ``method path``, or ``None``."""
    try:
        from django.urls import resolve
    except ImportError:  # pragma: no cover - the generator always runs inside Django
        return None
    for sample in _SAMPLES:
        try:
            match = resolve(_PARAM.sub(sample, path))
        except Exception:  # noqa: BLE001, S112 - Resolver404, no URLconf, settings not configured, ...
            continue
        func = match.func
        cls = getattr(func, "cls", None) or getattr(func, "view_class", None)
        if cls is None:
            return f"{func.__module__}.{getattr(func, '__qualname__', func.__name__)}"
        name = f"{cls.__module__}.{cls.__qualname__}"
        actions = getattr(func, "actions", None)
        action = actions.get(method.lower()) if isinstance(actions, dict) else None
        return f"{name}.{action}" if action else name
    return None


def describe(path: str, method: str, operation_id: str | None = None) -> str:
    """``POST /cfg/accounts/otp/verify/ (cfg_accounts_otp_verify_create, view …OTPViewSet.verify_otp)``."""
    details = [operation_id] if operation_id else []
    view = view_for(path, method)
    if view:
        details.append(f"view {view}")
    suffix = f" ({', '.join(details)})" if details else ""
    return f"{method.upper()} {path}{suffix}"


__all__ = ["describe", "view_for"]
