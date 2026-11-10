"""Reasoning-model token floor.

A model that reasons before answering spends part of ``max_tokens`` on a hidden
pass that never reaches ``content``. Under-budget it returns an empty
``content`` with ``finish_reason: "length"`` -- which reads as a model that
answered with nothing rather than one that was cut off, and every attempt is
billed. ``REASONING_MIN_MAX_TOKENS`` is the floor; ``min_max_tokens_for()``
applies it.

Keyed by the model SLUG FAMILY (``gpt-5``, ``o1-``...), not by provider or
alias: ``openai/gpt-4o-mini`` on the same endpoint needs no floor. Extend
``_REASONING_MODEL_MARKERS`` for a new family.
"""

from __future__ import annotations

from typing import Final

#: Floor for ``max_tokens`` on any model that reasons before answering.
#:
#: Measured 2026-09-03 on the dedup adjudicator's real payload against
#: ``openai/gpt-5-nano``: 300 and 800 both returned empty ``content`` with
#: ``finish_reason="length"``; 2000 answered.
REASONING_MIN_MAX_TOKENS: Final = 2000

#: Model-name fragments that identify a reasoning family. Matched on the id, so
#: ``openai/gpt-5-nano`` and a bare ``gpt-5-mini`` both hit.
_REASONING_MODEL_MARKERS: Final = ("gpt-5", "gpt-6", "o1-", "o3-", "o4-")


def is_reasoning_model(model: str | None) -> bool:
    """Whether ``model`` spends budget on a hidden pass before ``content``."""
    if not model:
        return False
    name = model.lower()
    return any(marker in name for marker in _REASONING_MODEL_MARKERS)


def min_max_tokens_for(model: str | None, requested: int) -> int:
    """Raise ``requested`` to the floor when ``model`` reasons before answering.

    Unchanged for everything else -- inflating a ceiling that is doing its job
    only hides genuine over-long output.
    """
    if is_reasoning_model(model):
        return max(requested, REASONING_MIN_MAX_TOKENS)
    return requested
