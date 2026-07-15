"""Serialise JSON-safe Python objects for LLM consumption.

We use TOON (Token-Oriented Object Notation, official toon-format
spec impl) for tabular replies — uniform arrays of scalar-only
objects, where it cuts ~20–25% of tokens vs minified JSON (measured
with tiktoken o200k_base on real CRM payloads) — and minified JSON
for everything else (envelopes, scalars, rows with nested lists or
dicts where TOON either doesn't help or actively hurts).

Format selection is a tool-level concern; this module exposes only
``serialize_for_llm`` and a tight heuristic for ``prefer="auto"``.

The ``toon_format`` package is a hard dependency. The import-fallback
below is a safety net for CI / dev installs that haven't synced deps
yet — production must always have it installed.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Literal


logger = logging.getLogger(__name__)

Format = Literal["toon", "json", "auto"]

# ``toon_format`` is the intended serializer, but it is an OPTIONAL harness dep:
# a host that hasn't installed the ``ai`` extra (or is mid-sync) must still be able
# to import the agent plane — TOON is a token optimisation, never a correctness
# requirement, and every caller already tolerates JSON. A bare import here made the
# whole agent plane fail to import on such a host (django-cfg hit exactly this), which
# is the opposite of what the docstring above promises. Absent → TOON is simply never
# chosen and we emit JSON, with one warning at import so the miss is visible.
try:
    from toon_format import encode as _toon_encode
except ImportError:  # pragma: no cover - exercised only where the extra is absent
    _toon_encode = None
    logger.warning(
        "toon_format not installed — the agent plane will serialise tool output as "
        "JSON (TOON token savings unavailable). Install the harness 'ai' extra to "
        "enable it."
    )


def serialize_for_llm(obj: Any, *, prefer: Format = "auto") -> str:
    """Serialise ``obj`` to a string the LLM can ingest.

    ``obj`` MUST be JSON-safe — call ``model.model_dump(mode="json")``
    upstream, not ``model_dump()`` (which leaves ``UUID`` / ``datetime``
    as Python objects that the encoders would refuse).

    Args:
        obj: JSON-safe dict / list / scalar.
        prefer:
            ``"json"`` — always minified JSON.
            ``"toon"`` — TOON when available; JSON fallback (warned).
            ``"auto"`` — TOON only when ``obj`` looks like a uniform
            scalar-only row table; JSON otherwise.
    """
    fmt = _resolve_format(obj, prefer)
    if fmt == "toon" and _toon_encode is not None:
        try:
            return _toon_encode(obj)
        except Exception as exc:
            # Don't crash a chat turn over a serialisation hiccup —
            # log and emit JSON instead. The agent never sees the
            # error. This catch is for unexpected payload shapes the
            # heuristic missed, NOT for missing-dependency cases.
            logger.warning(
                "toon_format encode failed (%s); falling back to JSON", exc,
            )
    return json.dumps(obj, separators=(",", ":"), default=str)


def _resolve_format(obj: Any, prefer: Format) -> Format:
    if prefer == "json":
        return "json"
    if prefer == "toon":
        return "toon"
    # auto: top-level dict with "items": [homogeneous, scalar-only rows]
    # → TOON. TOON's tabular compression kicks in only when every row
    # value is a scalar (str/int/float/bool/None); a nested list or
    # dict inside the row forces TOON into a YAML-ish layout that's
    # actually larger than minified JSON. So we check both shapes.
    if isinstance(obj, dict):
        items = obj.get("items")
        if (
            isinstance(items, list)
            and items
            and all(isinstance(x, dict) for x in items)
        ):
            keys = set(items[0].keys())
            if all(set(x.keys()) == keys for x in items) and all(
                _is_scalar(v) for row in items for v in row.values()
            ):
                return "toon"
    return "json"


def _is_scalar(v: Any) -> bool:
    return isinstance(v, (str, int, float, bool)) or v is None
