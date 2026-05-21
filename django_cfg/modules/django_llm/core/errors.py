"""
Typed error taxonomy for django_llm.

Every failure the module surfaces is an ``LLMError``. Raw provider /
openai-SDK exceptions are mapped into this hierarchy by
``classify_exception()`` so the retry/router layer decides retry vs
fail-fast from a typed ``.retryable`` flag — never by string-matching
error messages.

Host-agnostic: classification works off HTTP status codes, exception
class names, and message substrings, so no provider SDK import is needed.
"""

from __future__ import annotations

from typing import Any


class LLMError(Exception):
    """Base for every django_llm failure.

    Attributes:
        retryable: class-level — whether a retry might plausibly succeed.
        provider / model / attempt / request_id / status_code: call
            context, filled in when known.
        cost_incurred: USD already billed for the failed attempt — a
            response that arrived then failed validation was still paid.
        raw: the original exception, kept for debugging.
    """

    retryable: bool = False

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        attempt: int | None = None,
        request_id: str | None = None,
        status_code: int | None = None,
        cost_incurred: float = 0.0,
        raw: BaseException | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.model = model
        self.attempt = attempt
        self.request_id = request_id
        self.status_code = status_code
        self.cost_incurred = cost_incurred
        self.raw = raw


# ── Fatal — retrying the request will not help ────────────────────────────

class LLMConfigError(LLMError):
    """Module misconfiguration — missing key, unknown provider."""


class LLMAuthError(LLMError):
    """401 / 403 — credentials rejected."""


class LLMBadRequestError(LLMError):
    """400 / 404 / 422 — the request itself is malformed."""


class LLMCreditsError(LLMError):
    """402 — the provider account is out of credits."""


class LLMContentFilterError(LLMError):
    """The provider refused the request on a content policy."""


class LLMValidationError(LLMError):
    """A response arrived but failed JSON / schema validation."""


class LLMTruncationError(LLMError):
    """Output was cut off — ``finish_reason == 'length'``."""


class LLMBudgetError(LLMError):
    """A local spend cap was hit before the call was made."""


class AllProvidersFailedError(LLMError):
    """Every model / provider in the fallback chain failed.

    ``attempts`` is the per-model error list accumulated by the router.
    """

    def __init__(self, message: str, attempts: list[dict] | None = None, **kw: Any) -> None:
        super().__init__(message, **kw)
        self.attempts = attempts or []


# ── Transient — a retry (same or next model) may succeed ──────────────────

class LLMTransportError(LLMError):
    """Network / connection failure."""

    retryable = True


class LLMTimeoutError(LLMTransportError):
    """The request timed out."""

    retryable = True


class LLMServerError(LLMTransportError):
    """Provider-side 5xx."""

    retryable = True


class LLMRateLimitError(LLMTransportError):
    """429 — rate limited. ``retry_after`` is seconds to wait, when known."""

    retryable = True

    def __init__(self, message: str, *, retry_after: int | None = None, **kw: Any) -> None:
        super().__init__(message, **kw)
        self.retry_after = retry_after


# ── Classification ───────────────────────────────────────────────────────

_RETRYABLE_STATUS = frozenset({408, 409, 429, 500, 502, 503, 504, 529})


def _status_of(exc: BaseException) -> int | None:
    """Best-effort HTTP status from an SDK exception."""
    for attr in ("status_code", "status", "http_status"):
        val = getattr(exc, attr, None)
        if isinstance(val, int):
            return val
    return None


def _retry_after_of(exc: BaseException) -> int | None:
    """Best-effort Retry-After (seconds) from an SDK exception's headers."""
    headers = getattr(getattr(exc, "response", None), "headers", None)
    if not hasattr(headers, "get"):
        return None
    for key in ("retry-after", "Retry-After", "x-ratelimit-reset"):
        val = headers.get(key)
        if val:
            try:
                return int(float(val))
            except (ValueError, TypeError):
                pass
    return None


def classify_exception(
    exc: BaseException,
    *,
    provider: str | None = None,
    model: str | None = None,
    attempt: int | None = None,
) -> LLMError:
    """Map any exception to the django_llm taxonomy.

    An already-typed ``LLMError`` is returned unchanged, with missing
    call context filled in. Everything else is inspected by HTTP status,
    exception class name, then — defensively — message substring.
    """
    if isinstance(exc, LLMError):
        exc.provider = exc.provider or provider
        exc.model = exc.model or model
        if exc.attempt is None:
            exc.attempt = attempt
        return exc

    status = _status_of(exc)
    ctx: dict[str, Any] = dict(
        provider=provider, model=model, attempt=attempt,
        status_code=status, raw=exc,
    )
    msg = str(exc)
    low = msg.lower()
    cls_name = type(exc).__name__

    # Timeout / connection — checked first; these often carry no status.
    if cls_name in ("APITimeoutError", "Timeout") or "timed out" in low or "timeout" in low:
        return LLMTimeoutError(msg, **ctx)
    if cls_name == "APIConnectionError" or any(k in low for k in (
        "connection refused", "connection reset", "connection error",
        "name resolution", "eof occurred",
    )):
        return LLMTransportError(msg, **ctx)

    # By HTTP status (most reliable signal).
    if status == 402 or ("402" in msg and ("credit" in low or "insufficient" in low)):
        return LLMCreditsError(msg, **ctx)
    if status == 429 or "rate limit" in low or "too many requests" in low:
        return LLMRateLimitError(msg, retry_after=_retry_after_of(exc), **ctx)
    if status in (401, 403) or "invalid api key" in low or "unauthorized" in low:
        return LLMAuthError(msg, **ctx)
    if status in (400, 404, 422) or "model not found" in low:
        return LLMBadRequestError(msg, **ctx)
    if status in _RETRYABLE_STATUS or (status is not None and 500 <= status <= 599):
        return LLMServerError(msg, **ctx)
    if any(k in low for k in ("content filter", "content policy", "flagged", "moderation")):
        return LLMContentFilterError(msg, **ctx)

    # Unknown — surface as the non-retryable base error.
    return LLMError(msg, **ctx)
