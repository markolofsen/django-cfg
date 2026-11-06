"""Exception -> the widget's error code.

The widget knows three codes (`unavailable`, `timeout`, `failed`) and maps each to its
own sentence; the exception text never travels. Product-free: it reads only
pydantic-ai's and the standard library's exception types.
"""

from __future__ import annotations

#: Default customer-facing sentence per code, English. A host overrides them (and
#: translates them) by passing its own mapping to the driver.
DEFAULT_ERROR_MESSAGES: dict[str, str] = {
    "unavailable": "The assistant is unavailable right now. Please try again in a moment.",
    "timeout": "The answer took too long. Please try again.",
    "failed": "Something went wrong while answering. Please try again.",
}


def error_code_for(exc: BaseException) -> str:
    """`timeout` for a clock or wait that ran out, `unavailable` for a provider that
    could not serve (5xx, 408, 429, transport), `failed` for everything else
    (including a usage limit: the run did what it was allowed to and stopped)."""
    if isinstance(exc, TimeoutError):  # asyncio.TimeoutError is an alias since 3.11
        return "timeout"
    try:
        from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError
    except Exception:  # noqa: BLE001 - pydantic-ai is the plane's dependency, but never fail the mapping
        return "failed"
    if isinstance(exc, ModelHTTPError):
        status = int(getattr(exc, "status_code", 0) or 0)
        return "unavailable" if status >= 500 or status in (408, 429) else "failed"
    if isinstance(exc, ModelAPIError):
        return "unavailable"
    return "failed"
