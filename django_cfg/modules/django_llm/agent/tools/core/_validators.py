"""Small argument validators shared across tools.

Zero Django dependency — pure stdlib + the local ToolError schema.
"""

from __future__ import annotations

import uuid

from .schemas.base import ToolError, ToolErrorException


def parse_uuid(value: str, *, field: str = "id") -> uuid.UUID:
    """Coerce an LLM-supplied id string to a ``uuid.UUID``.

    The model routinely passes an email, name, or label where a UUID is
    expected. Feeding that straight into ``.get(pk=…)`` raises deep in the
    ORM (``ValidationError`` / ``ValueError: badly formed hexadecimal UUID
    string``), which the tool framework logs as a full stack trace before
    converting to a generic error. Raising ``ToolErrorException`` here routes
    through the clean error path instead — no traceback, and the agent gets a
    precise, actionable message it can recover from.
    """
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        raise ToolErrorException(
            ToolError(error=f"{field} is not a valid UUID: {value!r}")
        )


__all__ = ["parse_uuid"]
