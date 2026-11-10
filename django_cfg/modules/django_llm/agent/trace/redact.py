"""The redaction stage: what of a step may leave the server, per detail level. Fail closed.

Levels (`ChatKind.trace_level`): 0 records nothing; 1 codes, labels and summaries; 2 adds purpose, query, and the arguments and
result a tool DECLARED a view for (`ToolTrace`); 3 (admin only) adds generic detail for undeclared tools. Every level masks
secrets by key name and by shape. `shape_step` runs when a step is recorded and again when a stored trace is read (with the
reader's own level, which can only lower the stored one), so the live frame and the stored document cannot disagree.

If the redactor itself fails, the step is reduced to name, kind and status with `redaction="omitted"`: a bug costs detail, never a leak.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Protocol

from django_cfg.modules.django_llm.agent.trace.step import Redaction, StepRef, StepResult, TraceStep

log = logging.getLogger(__name__)

MASK = "[masked]"
MAX_LEVEL = 3
ARG_STR = {2: 200, 3: 1000}  # characters of one string value
PREVIEW = {2: 500, 3: 500}
MAX_ITEMS = 8
MAX_DEPTH = 3
MAX_TEXT = 200  # purpose, query, summary, label

_SENSITIVE_KEY = re.compile(r"pass(word|wd)?|secret|token|authori[sz]ation|api[_-]?key|cookie|credential|private[_-]?key|session|bearer|otp|pin\b", re.I)
_SECRETS = (
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\beyJ[\w-]{6,}\.[\w-]{6,}\.[\w-]{6,}"),  # a JWT
    re.compile(r"\b(?:\d[ -]?){13,19}\b"),  # a card-like digit run
    re.compile(r"\b[A-Za-z0-9_-]{32,}\b"),  # a long opaque token
)
_PERSONAL = (
    re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),  # an email
    re.compile(r"\+?\d[\d ().-]{8,}\d"),  # a phone
)


class Redactor(Protocol):
    """`(step, level) -> step`. May raise; the caller then drops the step's detail."""

    def __call__(self, step: TraceStep, level: int) -> TraceStep: ...


def mask_text(text: str, level: int = 2) -> str:
    """Secrets are masked at every level; emails and phones below level 3 (an admin may see them)."""
    out = text
    for pattern in _SECRETS:
        out = pattern.sub(MASK, out)
    if level < MAX_LEVEL:
        for pattern in _PERSONAL:
            out = pattern.sub(MASK, out)
    return out


def _clip(text: str, limit: int) -> tuple[str, bool]:
    text = " ".join(str(text).split())
    return (text, False) if len(text) <= limit else (text[: limit - 1] + "…", True)


def bound(value: Any, level: int, depth: int = 0) -> Any:
    """A bounded, masked copy of a JSON-like value: sensitive keys masked, long strings and big containers cut."""
    if isinstance(value, str):
        return mask_text(_clip(value, ARG_STR[level])[0], level)
    if isinstance(value, dict):
        if depth >= MAX_DEPTH:
            return f"{{{len(value)} keys}}"
        out: dict[str, Any] = {}
        for key, item in list(value.items())[:MAX_ITEMS]:
            name = str(key)[:60]
            out[name] = MASK if _SENSITIVE_KEY.search(name) else bound(item, level, depth + 1)
        if len(value) > MAX_ITEMS:
            out["…"] = f"{len(value) - MAX_ITEMS} more keys"
        return out
    if isinstance(value, (list, tuple)):
        if depth >= MAX_DEPTH:
            return f"[{len(value)} items]"
        items = [bound(v, level, depth + 1) for v in list(value)[:MAX_ITEMS]]
        if len(value) > MAX_ITEMS:
            items.append(f"… {len(value) - MAX_ITEMS} more")
        return items
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return mask_text(_clip(repr(value), ARG_STR[level])[0], level)


def _line(text: str | None, level: int) -> str | None:
    if text is None:
        return None
    return mask_text(_clip(text, MAX_TEXT)[0], level)


def omitted(step: TraceStep) -> TraceStep:
    """The fail-closed form: identity, timing and outcome only."""
    return step.model_copy(update={
        "args": None, "args_size": None, "result": None, "purpose": None, "query": None, "refs": [],
        "summary": "", "label": step.label if _safe_label(step.label) else "", "redaction": Redaction.OMITTED,
    })


def _safe_label(label: str) -> bool:
    return mask_text(label, 1) == label  # a label that would be masked is not a label


class DefaultRedactor:
    """Key and shape masking with the level rules above. A step arrives carrying the tool's DECLARED views (or none)."""

    def __call__(self, step: TraceStep, level: int) -> TraceStep:
        if level <= 0:
            raise ValueError("level 0 records nothing")
        level = min(level, MAX_LEVEL)
        changed = False

        def line(text: str | None) -> str | None:
            nonlocal changed
            out = _line(text, level)
            changed = changed or out != text
            return out

        # `redaction` speaks of the detail (arguments, result, purpose, query); a masked label or summary does not change it
        update: dict[str, Any] = {"label": _line(step.label, level) or "", "summary": _line(step.summary, level) or ""}
        shown = False
        if level >= 2:
            update["purpose"], update["query"] = line(step.purpose), line(step.query)
            if step.args is not None:
                masked = bound(step.args, level)
                changed = changed or masked != step.args
                update["args"], shown = masked, True
            if step.result is not None and step.result.preview:
                preview = mask_text(_clip(step.result.preview, PREVIEW[level])[0], level)
                changed = changed or preview != step.result.preview
                update["result"] = StepResult(preview=preview, size=step.result.size, truncated=step.result.truncated or len(step.result.preview) > PREVIEW[level])
                shown = True
        else:
            update.update(args=None, args_size=None, purpose=None, query=None)
            update["result"] = StepResult(size=step.result.size) if step.result is not None else None
        update["refs"] = [StepRef(kind=r.kind, id=mask_text(r.id, level), title=_line(r.title, level)) for r in step.refs]
        update["redaction"] = Redaction.MASKED if changed else (Redaction.NONE if shown else Redaction.OMITTED)
        return step.model_copy(update=update)


_default = DefaultRedactor()


def shape_step(step: TraceStep, level: int, redactor: Redactor | None = None) -> TraceStep:
    """The step as a reader at `level` may see it. Never raises: a failing redactor yields the `omitted` form."""
    try:
        return (redactor or _default)(step, level)
    except Exception:  # noqa: BLE001 - fail closed
        log.exception("trace: the redactor failed on a %s step; its detail is dropped", step.kind)
        try:
            return omitted(step)
        except Exception:  # noqa: BLE001
            return TraceStep(trace_id=step.trace_id, step_id=step.step_id, seq=step.seq, kind=step.kind, status=step.status)


def shape_doc(doc: dict | None, level: int, redactor: Redactor | None = None) -> dict | None:
    """A stored trace for a reader at `level` (never above the level it was recorded at). None when there is nothing to show."""
    from django_cfg.modules.django_llm.agent.trace.step import TraceDoc

    if not doc or level <= 0:
        return None
    try:
        parsed = TraceDoc.model_validate(doc)
    except Exception:  # noqa: BLE001 - a stored value this code cannot read is not shown
        log.warning("trace: a stored trace does not parse; not shown")
        return None
    effective = min(level, parsed.level) if parsed.level else 0
    if effective <= 0:
        return None
    parsed.steps = [shape_step(s, effective, redactor) for s in parsed.steps]
    parsed.level = effective
    parsed.frames = {}  # stream positions are the server's bookkeeping, not part of what a reader sees
    out = parsed.model_dump(mode="json", exclude_none=True)
    out.pop("frames", None)
    return out

