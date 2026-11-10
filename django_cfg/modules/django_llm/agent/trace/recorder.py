"""The recorder: one answer's steps, bounded, shaped and idempotent. Pure: no model, no Django, no I/O.

`begin` opens a step, `end` settles it, `add` records an instant one. Each change shapes the step at the recorder's level
(`redact.shape_step`) and queues a snapshot for the wire (`drain`), so what is sent and what is stored are the same bytes.
Raw detail (arguments, result text) lives only in the open step, in memory, until it settles.

Caps: 60 steps, 20 refs per step, 24 KB per document. A cap sets `truncated` and drops the newest detail, never the header.
`finish` is idempotent and settles whatever is still running.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from django_cfg.modules.django_llm.agent.bus.events import TraceStepEvent
from django_cfg.modules.django_llm.agent.trace.redact import Redactor, shape_step
from django_cfg.modules.django_llm.agent.trace.step import (
    SCHEMA_VERSION,
    DocStatus,
    Redaction,
    StepError,
    StepKind,
    StepRef,
    StepResult,
    StepStatus,
    StepTokens,
    ToolRole,
    TraceDoc,
    TraceErrorCode,
    TraceStep,
)

MAX_STEPS = 60
MAX_REFS = 20
MAX_BYTES = 24 * 1024

_RETRYABLE = {TraceErrorCode.PROVIDER_UNAVAILABLE, TraceErrorCode.PROVIDER_RATE_LIMITED, TraceErrorCode.TOOL_TIMEOUT, TraceErrorCode.TOOL_ERROR}
#: The widget's three user codes, as the typed cause the run ended with when nothing more exact was recorded.
_USER_CODE = {"timeout": TraceErrorCode.LIMIT, "unavailable": TraceErrorCode.PROVIDER_UNAVAILABLE}


def step_wire(step: TraceStep) -> dict[str, Any]:
    """One step as the wire and the stored document carry it."""
    return step.model_dump(mode="json", exclude_none=True)


def error_of(code: TraceErrorCode | str, retryable: bool | None = None) -> StepError:
    code = TraceErrorCode(code)
    return StepError(code=code, retryable=code in _RETRYABLE if retryable is None else retryable)


class Recorder:
    def __init__(
        self,
        level: int,
        *,
        model: str = "",
        guided_by: str | None = None,
        redactor: Redactor | None = None,
        clock: Callable[[], float] = time.monotonic,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        trace_id: str | None = None,
    ) -> None:
        self.level = max(0, min(int(level), 3))
        self.trace_id = trace_id or uuid.uuid4().hex[:16]
        self.wake = asyncio.Event()
        self._redactor = redactor
        self._clock = clock
        self._t0 = clock()
        self._doc = TraceDoc(trace_id=self.trace_id, level=self.level, started_at=now().isoformat(), model=model, guided_by=guided_by)
        self._open: dict[str, TraceStep] = {}  # raw, still running
        self._done: dict[str, TraceStep] = {}  # shaped
        self._order: list[str] = []
        self._outbox: list[TraceStepEvent] = []
        self._bytes = 0
        self._counter = 0
        self._closed = False

    # ── recording ───────────────────────────────────────────────────────────────

    @property
    def closed(self) -> bool:
        return self._closed

    def _ms(self) -> int:
        return int((self._clock() - self._t0) * 1000)

    def begin(
        self,
        kind: StepKind,
        *,
        name: str = "",
        parent_id: str | None = None,
        role: ToolRole | None = None,
        label: str = "",
        args: dict | None = None,
        args_size: int | None = None,
        purpose: str | None = None,
        query: str | None = None,
    ) -> str | None:
        """Open a step; returns its id, or None when nothing is recorded (level 0, closed, or a cap was reached)."""
        if self.level <= 0 or self._closed:
            return None
        self._counter += 1
        self._doc.steps_count = self._counter
        if self._counter > MAX_STEPS:
            self._doc.truncated = True
            return None
        step = TraceStep(
            trace_id=self.trace_id, step_id=f"s{self._counter}", seq=self._counter, parent_id=parent_id, kind=kind,
            name=name, role=role, label=label, started_ms=self._ms(), args=args, args_size=args_size, purpose=purpose, query=query,
        )
        self._open[step.step_id] = step
        self._order.append(step.step_id)
        self._publish(step)
        return step.step_id

    def end(
        self,
        step_id: str | None,
        status: StepStatus,
        *,
        error: StepError | None = None,
        summary: str | None = None,
        result_text: str | None = None,
        preview: str | None = None,
        tokens: StepTokens | None = None,
        cost_usd: float | None = None,
        refs: list[StepRef] | None = None,
        args: dict | None = None,
        purpose: str | None = None,
    ) -> None:
        """Settle an open step. `result_text` is the tool's raw text (only its size is kept); `preview` is its declared view."""
        if step_id is None:
            return
        step = self._open.pop(step_id, None)
        if step is None:
            return  # already settled, or never opened: ending twice is harmless
        update: dict[str, Any] = {"status": status, "duration_ms": max(0, self._ms() - step.started_ms)}
        if error is not None:
            update["error"] = error
        if summary is not None:
            update["summary"] = summary
        if result_text is not None or preview is not None:
            size = len(result_text) if result_text is not None else len(preview or "")
            shown = preview if preview is not None else ""
            update["result"] = StepResult(preview=shown, size=size, truncated=len(shown) < size and bool(shown))
        if tokens is not None:
            update["tokens"] = tokens
        if cost_usd is not None:
            update["cost_usd"] = cost_usd
        if refs:
            kept = refs[:MAX_REFS]
            if len(refs) > MAX_REFS:
                self._doc.truncated = True
            update["refs"] = kept
        if args is not None:
            update["args"] = args
        if purpose is not None:
            update["purpose"] = purpose
        self._publish(step.model_copy(update=update), settled=True)

    def add(self, kind: StepKind, status: StepStatus, **fields: Any) -> str | None:
        """An instant step (a guardrail trip, an error, the closing usage)."""
        error = fields.pop("error", None)
        tokens = fields.pop("tokens", None)
        cost = fields.pop("cost_usd", None)
        step_id = self.begin(kind, **fields)
        self.end(step_id, status, error=error, tokens=tokens, cost_usd=cost)
        return step_id

    def _publish(self, raw: TraceStep, *, settled: bool = False) -> None:
        shaped = shape_step(raw, self.level, self._redactor)
        if settled:
            shaped = self._within_budget(shaped)
            previous = self._done.get(shaped.step_id)
            if previous is not None:
                self._bytes -= len(json.dumps(step_wire(previous)))
            self._done[shaped.step_id] = shaped
            self._bytes += len(json.dumps(step_wire(shaped)))
        else:
            self._open[raw.step_id] = raw
        self._outbox.append(TraceStepEvent(step=step_wire(shaped)))
        self.wake.set()

    def _within_budget(self, step: TraceStep) -> TraceStep:
        """Keep the document under `MAX_BYTES`: past it a settled step loses its detail, and says so."""
        if self._bytes + len(json.dumps(step_wire(step))) <= MAX_BYTES:
            return step
        self._doc.truncated = True
        return step.model_copy(update={"args": None, "args_size": step.args_size, "result": None, "purpose": None, "query": None, "refs": [], "redaction": Redaction.OMITTED})

    # ── the wire ────────────────────────────────────────────────────────────────

    def drain(self) -> list[TraceStepEvent]:
        """The frames queued since the last call, oldest first."""
        out, self._outbox = self._outbox, []
        self.wake.clear()
        return out

    # ── closing ─────────────────────────────────────────────────────────────────

    def finish(
        self,
        status: str,
        error_code: str = "",
        *,
        tokens_in: int | None = None,
        tokens_out: int | None = None,
        cost_usd: float | None = None,
        model: str | None = None,
    ) -> None:
        """Close the trace once: settle what still runs, record the cause of an error and the usage totals. Later calls do nothing."""
        if self._closed or self.level <= 0:
            self._closed = True
            return
        stopped = StepStatus.CANCELLED if status == "cancelled" else StepStatus.ERROR
        for step_id in list(self._open):
            self.end(step_id, stopped, error=error_of(TraceErrorCode.CANCELLED) if stopped is StepStatus.CANCELLED else None)
        if status == "error" and not any(s.kind is StepKind.ERROR for s in self._done.values()):
            cause = self._cause() or _USER_CODE.get(error_code)
            if cause is not None:
                self.add(StepKind.ERROR, StepStatus.ERROR, name="run", label="The answer failed", error=error_of(cause))
        if tokens_in is not None or tokens_out is not None or cost_usd is not None:
            self.add(StepKind.USAGE, StepStatus.OK, name="usage", label="Usage", tokens=StepTokens(input=tokens_in, output=tokens_out), cost_usd=cost_usd)
        self._closed = True
        self._doc.status = {"done": DocStatus.DONE, "error": DocStatus.ERROR}.get(status, DocStatus.CANCELLED)
        if model:
            self._doc.model = model

    def _cause(self) -> TraceErrorCode | None:
        """The typed cause of the last failed step, when one was recorded (a provider failure on a model step)."""
        for step_id in reversed(self._order):
            step = self._done.get(step_id)
            if step is not None and step.error is not None and step.kind is StepKind.MODEL:
                return step.error.code
        return None

    # ── reading ─────────────────────────────────────────────────────────────────

    def doc(self) -> dict[str, Any]:
        """The document as stored: header plus the steps that have settled (a running one is shown as it stands)."""
        steps = [self._done.get(i) or self._shaped_open(i) for i in self._order]
        self._doc.steps = [s for s in steps if s is not None]
        return self._doc.model_dump(mode="json", exclude_none=True)

    def _shaped_open(self, step_id: str) -> TraceStep | None:
        raw = self._open.get(step_id)
        return shape_step(raw, self.level, self._redactor) if raw is not None else None


__all__ = ["MAX_BYTES", "MAX_REFS", "MAX_STEPS", "SCHEMA_VERSION", "Recorder", "error_of", "step_wire"]
