"""The answer's trace: TraceStep v1, the recorder, the capability that fills it, the redactor and the sink. See `@docs/trace.md`."""

from django_cfg.modules.django_llm.agent.trace.recorder import MAX_BYTES, MAX_REFS, MAX_STEPS, Recorder, error_of, step_wire
from django_cfg.modules.django_llm.agent.trace.redact import DefaultRedactor, Redactor, shape_doc, shape_step
from django_cfg.modules.django_llm.agent.trace.sink import MessageJsonSink, TraceSink
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
from django_cfg.modules.django_llm.agent.trace.tooltrace import ToolTrace

__all__ = [
    "MAX_BYTES", "MAX_REFS", "MAX_STEPS", "SCHEMA_VERSION",
    "DefaultRedactor", "DocStatus", "MessageJsonSink", "Recorder", "Redaction", "Redactor", "StepError", "StepKind", "StepRef", "StepResult",
    "StepStatus", "StepTokens", "ToolRole", "ToolTrace", "TraceDoc", "TraceErrorCode", "TraceSink", "TraceStep",
    "error_of", "shape_doc", "shape_step", "step_wire",
]
