"""Validate-and-repair for structured LLM output.

The local half of the pipeline from
``@docs/insights/structured-output.md``:

```
content (+ finish_reason)
  -> json.loads + Pydantic validate
       ok                       -> return instance
       finish_reason == length  -> raise LLMTruncationError   (caller bumps max_tokens)
       syntax damage            -> json-repair, re-parse, re-validate
            repaired ok         -> return instance
            still broken        -> raise LLMValidationError    (caller may re-ask)
       semantic failure         -> raise LLMValidationError    (caller may re-ask)
```

A local repair costs ~nothing next to a re-ask (which is a full extra billed
call at ~200× the latency), so we always repair-before-reask. We never repair
a **truncation** — ``finish_reason == 'length'`` means data is genuinely
missing; repairing it would fabricate a plausible-but-wrong object and hide
the loss. The caller raises ``max_tokens`` and retries instead.

The network half (the bounded re-ask on semantic failure) lives in
``routing/llm_router.py`` because it needs the client; this module stays pure
and unit-testable.
"""

from __future__ import annotations

import json
import logging
import re
from typing import TypeVar

from json_repair import repair_json
from pydantic import BaseModel, ValidationError

from ..core.errors import LLMTruncationError, LLMValidationError

logger = logging.getLogger("django_cfg.django_llm.repair")

T = TypeVar("T", bound=BaseModel)

# Smart/curly double-quotes some models emit inside JSON → straight. Kept in
# lockstep with structured/extractor.py and the router so all three normalise
# identically before parsing.
_QUOTE_FIXES = (("“", '"'), ("”", '"'), ("„", '"'), ("‟", '"'))


def _strip_fences(content: str) -> str:
    """Drop a leading ```json / ``` fence and trailing ``` plus smart quotes."""
    c = (content or "").strip()
    if c.startswith("```"):
        c = re.sub(r"^```[^\n]*\n?", "", c)
        c = re.sub(r"```$", "", c).strip()
    for bad, good in _QUOTE_FIXES:
        c = c.replace(bad, good)
    return c


def parse_into_schema(
    content: str,
    schema: type[T],
    *,
    finish_reason: str | None = None,
    repair: bool = True,
) -> T:
    """Parse ``content`` into ``schema``, repairing syntactic damage.

    Args:
        content: Raw model text (may carry fences / preamble / trailing commas).
        schema: Target Pydantic model.
        finish_reason: The provider's finish reason. ``"length"`` short-circuits
            to ``LLMTruncationError`` — a truncated body is missing data, not
            dirty syntax, so it must NOT be repaired.
        repair: When False, skip the json-repair stage (strict parse only) —
            useful for tests and for callers that want a hard reject.

    Returns:
        A validated ``schema`` instance.

    Raises:
        LLMTruncationError: ``finish_reason == 'length'`` — caller should bump
            ``max_tokens`` and retry.
        LLMValidationError: parse or schema validation failed even after repair
            — caller may run one bounded re-ask with the error injected.
    """
    # 1. Truncation is a data-loss signal, not a syntax problem — never repair.
    if finish_reason == "length":
        raise LLMTruncationError(
            "Model output was cut off (finish_reason='length'); raise max_tokens."
        )

    cleaned = _strip_fences(content)

    # 2. Happy path — strict parse + validate.
    try:
        return schema.model_validate(json.loads(cleaned))
    except json.JSONDecodeError as exc:
        first_error: Exception = exc
    except ValidationError as exc:
        # Valid JSON, wrong shape → a semantic failure. Repair can't fix the
        # shape; surface it so the caller can re-ask with the error.
        raise LLMValidationError(
            f"{schema.__name__} validation failed: {exc}"
        ) from exc

    # 3. Syntactic damage — repair, then re-parse + re-validate.
    if repair:
        try:
            repaired = repair_json(cleaned)  # returns a JSON *string*
            obj = json.loads(repaired)
            instance = schema.model_validate(obj)
            logger.debug("parse_into_schema: recovered %s via json-repair", schema.__name__)
            return instance
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            first_error = exc

    raise LLMValidationError(
        f"Could not parse model output into {schema.__name__}: {first_error}"
    ) from first_error


__all__ = ["parse_into_schema"]
