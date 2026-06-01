"""Advisory layer — warns when a model is used against a role or request
shape the catalog knows it fails.

Advisory only: each check emits a ``warnings.warn`` + a log line and
returns the messages. It never blocks a call and never raises — a broken
advisory must not be able to break inference.
"""

from __future__ import annotations

import logging
import warnings

from .models import traits
from .roles import ModelRole, Verdict

logger = logging.getLogger(__name__)


class LLMAdvisory(UserWarning):
    """A non-fatal advisory about a risky model or request choice."""


# Dedup — one warning per (model, rule) per process. Advisories are
# guidance, not a per-call log spammer.
_seen: set[tuple[str, str]] = set()


def reset() -> None:
    """Clear the dedup memory. For tests."""
    _seen.clear()


def _emit(model: str, rule: str, message: str) -> None:
    if (model, rule) in _seen:
        return
    _seen.add((model, rule))
    warnings.warn(f"[django_llm] {model}: {message}", LLMAdvisory, stacklevel=3)
    logger.warning("llm advisory [%s] %s — %s", rule, model, message)


def _wants_strict_schema(response_format: object) -> bool:
    """True when the request asks for provider-enforced json_schema."""
    if isinstance(response_format, type):          # a Pydantic model class
        return True
    if isinstance(response_format, dict):
        return response_format.get("type") == "json_schema"
    return False


def check(
    model: str,
    *,
    role: ModelRole | None = None,
    response_format: object = None,
    model_array: bool = False,
    supported_parameters: list[str] | None = None,
) -> list[str]:
    """Inspect a model + request and emit advisories for known pitfalls.

    Returns the advisory messages (also ``warnings.warn``-ed and logged,
    deduped per process). Best-effort — never raises, never blocks.

    ``supported_parameters`` (from the live registry) enables the
    structured-output check; omit it to skip that one rule.
    """
    found: list[tuple[str, str]] = []
    try:
        t = traits(model)

        if role is ModelRole.EXTRACTION and t is not None and t.reasoning:
            found.append((
                "reasoning_in_extraction",
                "reasoning model in the EXTRACTION hot path — reasoning "
                "tokens hurt determinism, latency tails and cost predictability",
            ))

        if role is not None and t is not None and t.verdict(role) is Verdict.AVOID:
            why = "; ".join(t.issues) if t.issues else "graded AVOID"
            found.append((
                "avoid_verdict",
                f"catalog grades this AVOID for role={role.value} — {why}",
            ))

        if model_array:
            found.append((
                "model_array",
                "multi-model request array — OpenRouter downgrades to "
                "tool-calling emulation; strict json_schema is lost",
            ))

        if (_wants_strict_schema(response_format)
                and supported_parameters is not None
                and "structured_outputs" not in supported_parameters):
            found.append((
                "no_structured_outputs",
                "strict json_schema requested but the model/provider does "
                "not advertise structured_outputs — silent downgrade to "
                "plain json_object is likely",
            ))

        for rule, message in found:
            _emit(model, rule, message)
    except Exception:
        logger.debug("advisory check failed for %r", model, exc_info=True)

    return [message for _, message in found]
