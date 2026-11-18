"""Key-name redaction for structured log fields (``extra`` and monitor events)."""
from __future__ import annotations

from typing import Any, Iterable

MASK = "***"

DEFAULT_REDACT_KEYS = (
    "password", "passwd", "token", "secret", "authorization", "cookie", "set-cookie", "api_key", "apikey",
    "access_key", "private_key", "credential", "credentials", "bearer", "sessionid", "csrftoken",
)


def _is_secret(key: Any, needles: tuple) -> bool:
    k = "_" + str(key).lower().replace("-", "_") + "_"
    return any(f"_{n}_" in k for n in needles)  # whole segments: "access_token" yes, "max_tokens" no


def redact(value: Any, keys: Iterable[str] = DEFAULT_REDACT_KEYS, _depth: int = 0) -> Any:
    """Copy of ``value`` with the values of secret-looking keys masked, recursing into dicts/lists."""
    needles = tuple(str(k).lower().replace("-", "_") for k in keys)
    return _walk(value, needles, 0)


def _walk(value: Any, needles: tuple, depth: int) -> Any:
    if depth > 8:
        return value
    if isinstance(value, dict):
        return {k: (MASK if _is_secret(k, needles) else _walk(v, needles, depth + 1)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_walk(v, needles, depth + 1) for v in value]
    return value
