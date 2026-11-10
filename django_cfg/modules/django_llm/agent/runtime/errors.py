"""Exception -> the widget's error code, and the typed cause behind it.

The widget knows three codes (`unavailable`, `timeout`, `failed`) and maps each to its
own sentence; the exception text never travels. Behind that user code sits `ErrorInfo.code`,
the closed internal vocabulary an operator and the trace read (`provider_credit` is
"the account is out of money", which the user sees only as `unavailable`).
Product-free: it reads only pydantic-ai's and the standard library's exception types.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Default customer-facing sentence per code, English. A host overrides them (and
#: translates them) by passing its own mapping to the driver.
DEFAULT_ERROR_MESSAGES: dict[str, str] = {
    "unavailable": "The assistant is unavailable right now. Please try again in a moment.",
    "timeout": "The answer took too long. Please try again.",
    "failed": "Something went wrong while answering. Please try again.",
}


#: Internal causes of a provider failure (a subset of the trace's closed `error.code` vocabulary).
PROVIDER_UNAVAILABLE = "provider_unavailable"  # 5xx, 408, transport
PROVIDER_RATE_LIMITED = "provider_rate_limited"  # 429
PROVIDER_CREDIT = "provider_credit"  # 402: the account is out of credit
PROVIDER_AUTH = "provider_auth"  # 401 / 403: the key is refused
MODEL_RETIRED = "model_retired"  # 404 / 410: the slug no longer exists

#: Which cause to report when a fall-over chain fails with several: the one an operator must act on first.
_ACTION_ORDER = (PROVIDER_CREDIT, PROVIDER_AUTH, MODEL_RETIRED, PROVIDER_RATE_LIMITED, PROVIDER_UNAVAILABLE)

_HTTP_CAUSE = {402: PROVIDER_CREDIT, 401: PROVIDER_AUTH, 403: PROVIDER_AUTH, 404: MODEL_RETIRED, 410: MODEL_RETIRED, 429: PROVIDER_RATE_LIMITED, 408: PROVIDER_UNAVAILABLE}


@dataclass(frozen=True)
class ErrorInfo:
    user_code: str  # `unavailable` | `timeout` | `failed`: the widget's code
    code: str | None = None  # the typed provider cause, None for anything else
    retryable: bool = True  # a retry can help (false for credit, auth, retired)
    status: int = 0  # provider HTTP status, 0 when none
    model: str = ""  # the slug that failed, when the exception names it


def provider_cause(status: int) -> str | None:
    """The typed cause of a provider HTTP status, None when the status is not a provider-side failure (400 and 422 are ours)."""
    if status >= 500:
        return PROVIDER_UNAVAILABLE
    return _HTTP_CAUSE.get(status)


def _leaves(exc: BaseException) -> list[BaseException]:
    if isinstance(exc, BaseExceptionGroup):
        return [leaf for inner in exc.exceptions for leaf in _leaves(inner)]
    return [exc]


def _classify_one(exc: BaseException) -> ErrorInfo:
    if isinstance(exc, TimeoutError):  # asyncio.TimeoutError is an alias since 3.11
        return ErrorInfo("timeout")
    try:
        from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError
    except Exception:  # noqa: BLE001 - pydantic-ai is the plane's dependency, but never fail the mapping
        return ErrorInfo("failed")
    if isinstance(exc, ModelHTTPError):
        status = int(getattr(exc, "status_code", 0) or 0)
        cause = provider_cause(status)
        if cause is None:
            return ErrorInfo("failed", status=status, model=exc.model_name)
        return ErrorInfo("unavailable", cause, cause in (PROVIDER_UNAVAILABLE, PROVIDER_RATE_LIMITED), status, exc.model_name)
    if isinstance(exc, ModelAPIError):
        return ErrorInfo("unavailable", PROVIDER_UNAVAILABLE, True, 0, exc.model_name)
    return ErrorInfo("failed")


def classify(exc: BaseException) -> ErrorInfo:
    """What went wrong. A `FallbackExceptionGroup` (every model of a chain failed) is read by its members:
    the user code is `unavailable` when any member is a provider failure, and the cause is the one to act on first."""
    infos = [_classify_one(leaf) for leaf in _leaves(exc)]
    if len(infos) == 1:
        return infos[0]
    caused = [i for i in infos if i.code is not None]
    if caused:
        best = min(caused, key=lambda i: _ACTION_ORDER.index(i.code))
        return ErrorInfo("unavailable", best.code, best.retryable, best.status, best.model)
    for user_code in ("timeout", "failed"):
        if any(i.user_code == user_code for i in infos):
            return ErrorInfo(user_code)
    return ErrorInfo("failed")


def error_code_for(exc: BaseException) -> str:
    """`timeout` for a clock or wait that ran out, `unavailable` for a provider that
    could not serve (5xx, 408, 429, 402, 401, 403, a retired model, transport, or a whole fallback chain of those), `failed` for everything else
    (including a usage limit: the run did what it was allowed to and stopped)."""
    return classify(exc).user_code


def describe(exc: BaseException) -> str:
    """One log-safe line for a failure: the type, the provider status, the slug. Never `str(exc)`: a provider
    error carries the response body, which can echo the prompt."""
    info = classify(exc)
    parts = [type(exc).__name__]
    if info.code:
        parts.append(info.code)
    if info.status:
        parts.append(f"status={info.status}")
    if info.model:
        parts.append(f"model={info.model}")
    if isinstance(exc, BaseExceptionGroup):
        parts.append("members=[" + "; ".join(describe(leaf) for leaf in _leaves(exc)) + "]")
    return " ".join(parts)


def is_provider_failure(exc: BaseException) -> bool:
    """True when the failure is the provider's (or a whole chain of them): its traceback and body add nothing to the log."""
    return classify(exc).code is not None
