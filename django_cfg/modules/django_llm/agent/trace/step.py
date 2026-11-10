"""TraceStep v1: what one answer did, as data. One row per step, one document per answer.

The contract is versioned (`SCHEMA_VERSION`, also `TraceDoc.v`) and additive: a reader ignores a field it does not know. A step is
sent twice on the wire (`status=running`, then the settled row with the same `step_id`) and stored once, in its settled form.
Nothing here reads a request, a model or a database; the recorder fills it, the redactor shapes it, a sink stores it.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1


class StepKind(StrEnum):
    MODEL = "model"  # one request to the model
    REASONING = "reasoning"  # the model thought; its text is never recorded
    TOOL = "tool"
    APPROVAL = "approval"
    HANDOFF = "handoff"
    GUARDRAIL = "guardrail"
    SOURCE = "source"
    ERROR = "error"
    USAGE = "usage"  # the closing totals


class StepStatus(StrEnum):
    RUNNING = "running"
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    DENIED = "denied"


class ToolRole(StrEnum):
    RETRIEVER = "retriever"  # reads documents or a knowledge base: its refs are the answer's sources
    READ = "read"
    WRITE = "write"
    PROPOSE = "propose"  # prepares a change that a person confirms


class Redaction(StrEnum):
    NONE = "none"  # shown as it is
    MASKED = "masked"  # some values were replaced
    OMITTED = "omitted"  # no detail leaves the server (the fail-closed default)


class DocStatus(StrEnum):
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


class TraceErrorCode(StrEnum):
    """The closed vocabulary of `error.code`. A new cause is a new member here, in the docs and in the widget's table, together."""

    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_RATE_LIMITED = "provider_rate_limited"
    PROVIDER_CREDIT = "provider_credit"
    PROVIDER_AUTH = "provider_auth"
    MODEL_RETIRED = "model_retired"
    TOOL_ERROR = "tool_error"
    TOOL_TIMEOUT = "tool_timeout"
    BAD_TOOL_ARGS = "bad_tool_args"
    LOOP_DETECTED = "loop_detected"
    LIMIT = "limit"
    GUARD_TRIPPED = "guard_tripped"
    CONTENT_FILTER = "content_filter"
    OUTPUT_TRUNCATED = "output_truncated"
    EMPTY_ANSWER = "empty_answer"
    ATTACHMENT_UNREADABLE = "attachment_unreadable"
    CANCELLED = "cancelled"
    APPROVAL_UNSUPPORTED = "approval_unsupported"


class StepError(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: TraceErrorCode
    retryable: bool = False


class StepResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    preview: str = ""  # at most `limits.RESULT_PREVIEW` characters
    size: int = 0  # characters of the whole result
    truncated: bool = False


class StepTokens(BaseModel):
    model_config = ConfigDict(extra="ignore")

    input: int | None = None
    output: int | None = None
    reasoning: int | None = None
    cached: int | None = None


class StepRef(BaseModel):
    """What a step used: a document, a record, a page. The widget shows it as a source chip."""

    model_config = ConfigDict(extra="ignore")

    kind: str
    id: str
    title: str | None = None


class TraceStep(BaseModel):
    model_config = ConfigDict(extra="ignore")

    v: int = SCHEMA_VERSION
    trace_id: str
    step_id: str  # `s<n>`, unique in the trace
    seq: int  # 1, 2, 3 ... gap-free in order of start
    parent_id: str | None = None  # a tool's model step; a reasoning step's model step
    kind: StepKind
    status: StepStatus = StepStatus.RUNNING
    name: str = ""  # the tool name or the model slug
    role: ToolRole | None = None  # tool steps only
    label: str = ""  # one readable line for the step ("Searching the knowledge base")
    summary: str = ""  # one readable line for the outcome ("5 documents")
    started_ms: int = 0  # milliseconds since the trace began
    duration_ms: int | None = None
    args: dict[str, Any] | None = None  # a redacted view, never the raw arguments below level 3
    args_size: int | None = None
    result: StepResult | None = None
    redaction: Redaction = Redaction.OMITTED
    error: StepError | None = None
    purpose: str | None = None
    query: str | None = None
    tokens: StepTokens | None = None
    cost_usd: float | None = None
    refs: list[StepRef] = Field(default_factory=list)


class TraceDoc(BaseModel):
    """One answer's trace: the header and its steps. Stored as one JSON value on the message."""

    model_config = ConfigDict(extra="ignore")

    v: int = SCHEMA_VERSION
    trace_id: str
    level: int = 0
    started_at: str = ""  # ISO 8601, UTC
    status: DocStatus = DocStatus.RUNNING
    model: str = ""
    steps_count: int = 0  # steps recorded, including any dropped by a cap
    truncated: bool = False  # a cap dropped steps, refs or bytes
    guided_by: str | None = None  # the prompt version that steered the answer
    steps: list[TraceStep] = Field(default_factory=list)
    # step_id -> the stream position (SSE `id:`) of that step's newest frame; what a resume compares its `after` with.
    # Stored, never shown: `shape_doc` drops it. A step missing here is always sent by a resume.
    frames: dict[str, int] = Field(default_factory=dict)
