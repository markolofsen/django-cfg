"""Opaque base64-JSON cursors for keyset pagination.

Cursor contents are an array of values from `SitemapSource.cursor_fields`.
Datetime values are serialised as ISO 8601 strings; everything else as-is.

The cursor is opaque to the frontend — it just passes it through to the
feed endpoint. We keep the format simple and debuggable: a base64-decoded
cursor is a readable JSON array.
"""
from __future__ import annotations

import base64
import binascii
import json
import uuid
from datetime import date, datetime
from typing import Any


class CursorError(ValueError):
    """Raised on malformed cursor — view turns this into 400."""


def encode_cursor(values: tuple[Any, ...]) -> str:
    payload = [_jsonable(v) for v in values]
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode_cursor(token: str) -> tuple[Any, ...]:
    if not token:
        raise CursorError("empty cursor")
    padding = "=" * (-len(token) % 4)
    try:
        raw = base64.urlsafe_b64decode(token + padding)
        payload = json.loads(raw.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CursorError(f"malformed cursor: {exc}") from exc
    if not isinstance(payload, list):
        raise CursorError("cursor payload must be a JSON array")
    return tuple(payload)


def _jsonable(v: Any) -> Any:
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, uuid.UUID):
        return str(v)
    return v
