"""`TraceCapability`: turns a run's model requests and tool calls into steps of a `Recorder`.

One capability, composed OUTSIDE `tool_guard` so it sees the guard's `tool_timeout` / `tool_error` failures. It records timing,
status and the typed error code; the detail a step may carry is the tool's DECLARED view (`ToolTrace`) and the recorder's
redactor decides what leaves. It never reads `ThinkingPart` text (a reasoning step records only that the model thought and how
many tokens it spent). A hook that fails costs the step, never the answer.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Mapping
from typing import Any

from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.exceptions import ApprovalRequired, CallDeferred, ModelRetry, SkipToolExecution, ToolFailed, ToolRetryError, UsageLimitExceeded
from pydantic_ai.messages import TextPart, ThinkingPart

from django_cfg.modules.django_llm.agent.capabilities.tool_guard import TOOL_TIMEOUT
from django_cfg.modules.django_llm.agent.runtime.errors import classify
from django_cfg.modules.django_llm.agent.trace.recorder import Recorder, error_of
from django_cfg.modules.django_llm.agent.trace.step import StepKind, StepStatus, StepTokens, TraceErrorCode
from django_cfg.modules.django_llm.agent.trace.tooltrace import ToolTrace, generic_label, raw_args, role_for

log = logging.getLogger(__name__)

PURPOSE_CHARS = 200


def _text_of(result: Any) -> str:
    if isinstance(result, str):
        return result
    try:
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception:  # noqa: BLE001
        return str(result)


class TraceCapability(AbstractCapability[Any]):
    def __init__(self, recorder: Recorder, tools: Mapping[str, ToolTrace] | None = None, categories: Mapping[str, str] | None = None) -> None:
        self.recorder = recorder
        self.tools = dict(tools or {})
        self.categories = dict(categories or {})
        self._model_step: str | None = None
        self._issuer: str | None = None  # the model step whose response asked for the tool calls now running
        self._said = ""  # the visible text of the newest response: the stated reason of the calls that follow it

    # ── model requests ──────────────────────────────────────────────────────────

    async def before_model_request(self, ctx, request_context):
        try:
            slug = str(getattr(getattr(ctx, "model", None), "model_name", "") or "")
            self._model_step = self.recorder.begin(StepKind.MODEL, name=slug, label="Thinking")
        except Exception:  # noqa: BLE001
            log.exception("trace: could not open a model step")
        return request_context

    async def after_model_request(self, ctx, *, request_context, response):
        try:
            usage = getattr(response, "usage", None)
            details = getattr(usage, "details", None) or {}
            reasoning = details.get("reasoning_tokens") if isinstance(details, dict) else None
            self._said = " ".join(p.content.strip() for p in response.parts if isinstance(p, TextPart) and p.content.strip())
            step = self._model_step
            self.recorder.end(
                step, StepStatus.OK,
                tokens=StepTokens(input=getattr(usage, "input_tokens", None), output=getattr(usage, "output_tokens", None), reasoning=reasoning, cached=getattr(usage, "cache_read_tokens", None)),
            )
            if any(isinstance(p, ThinkingPart) for p in response.parts):  # that it thought; never what it thought
                self.recorder.add(StepKind.REASONING, StepStatus.OK, name="reasoning", label="Reasoning", parent_id=step, tokens=StepTokens(reasoning=reasoning) if reasoning else None)
            self._issuer, self._model_step = step, None
        except Exception:  # noqa: BLE001
            log.exception("trace: could not record a model step")
        return response

    async def on_model_request_error(self, ctx, *, request_context, error):
        self._model_failed(error)
        raise error

    async def on_run_error(self, ctx, *, error):
        """A streamed request fails while its stream is read, which `on_model_request_error` does not see: the run's own failure
        settles the open model step with the typed cause. A run that hit its usage limit is a `limit` step."""
        if not isinstance(error, asyncio.CancelledError):
            if self._model_step is not None:
                self._model_failed(error)
            elif isinstance(error, UsageLimitExceeded):
                self._safely(lambda: self.recorder.add(StepKind.ERROR, StepStatus.ERROR, name="run", label="The answer hit its limit", error=error_of(TraceErrorCode.LIMIT)))
        raise error

    def _model_failed(self, error: BaseException) -> None:
        def settle() -> None:
            info = classify(error)
            code = TraceErrorCode(info.code) if info.code else (TraceErrorCode.LIMIT if info.user_code == "timeout" else None)
            self.recorder.end(self._model_step, StepStatus.TIMEOUT if info.user_code == "timeout" else StepStatus.ERROR, error=error_of(code, info.retryable) if code else None)
            self._model_step = None

        self._safely(settle)

    @staticmethod
    def _safely(fn) -> None:
        try:
            fn()
        except Exception:  # noqa: BLE001 - the trace must not change how a run fails
            log.exception("trace: could not record a failure")

    # ── tool calls ──────────────────────────────────────────────────────────────

    async def on_tool_validate_error(self, ctx, *, call, tool_def, args, error):
        try:
            self.recorder.add(StepKind.TOOL, StepStatus.ERROR, name=call.tool_name, label=self._label(call.tool_name), parent_id=self._issuer, error=error_of(TraceErrorCode.BAD_TOOL_ARGS, True))
        except Exception:  # noqa: BLE001
            log.exception("trace: could not record a validation failure")
        raise error

    async def wrap_tool_execute(self, ctx, *, call, tool_def, args, handler):
        name = call.tool_name
        raw = raw_args(args)
        step = self._begin_tool(name, raw)
        try:
            result = await handler(args)
        except asyncio.CancelledError:
            self._end(step, StepStatus.CANCELLED, error_of(TraceErrorCode.CANCELLED))
            raise
        except ToolFailed as exc:
            timed_out = str(exc).startswith(TOOL_TIMEOUT)
            self._end(step, StepStatus.TIMEOUT if timed_out else StepStatus.ERROR, error_of(TraceErrorCode.TOOL_TIMEOUT if timed_out else TraceErrorCode.TOOL_ERROR))
            raise
        except (ModelRetry, ToolRetryError):
            self._end(step, StepStatus.ERROR, error_of(TraceErrorCode.BAD_TOOL_ARGS, True))
            raise
        except ApprovalRequired:
            self._end(step, StepStatus.SKIPPED, error_of(TraceErrorCode.APPROVAL_UNSUPPORTED))
            raise
        except (CallDeferred, SkipToolExecution):
            self._end(step, StepStatus.SKIPPED, None)
            raise
        except Exception:
            self._end(step, StepStatus.ERROR, error_of(TraceErrorCode.TOOL_ERROR))
            raise
        self._settle(step, name, raw, result, getattr(ctx, "deps", None))
        return result

    # ── helpers ─────────────────────────────────────────────────────────────────

    def _label(self, name: str) -> str:
        declared = self.tools.get(name)
        return declared.label if declared is not None else generic_label(name)

    def _begin_tool(self, name: str, raw: dict) -> str | None:
        try:
            declared = self.tools.get(name)
            level = self.recorder.level
            view: dict | None = None
            query = None
            if declared is not None:
                view = declared.view_args(raw)
                if declared.query_arg and isinstance(raw.get(declared.query_arg), str):
                    query = raw[declared.query_arg]
            if view is None and level >= 3:
                view = raw
            why = raw.get("why")
            purpose = (why if isinstance(why, str) and why.strip() else self._said)[:PURPOSE_CHARS] or None
            return self.recorder.begin(
                StepKind.TOOL, name=name, parent_id=self._issuer, role=role_for(name, declared, self.categories), label=self._label(name),
                args=view, args_size=len(_text_of(raw)), purpose=purpose, query=query,
            )
        except Exception:  # noqa: BLE001
            log.exception("trace: could not open a tool step")
            return None

    def _end(self, step: str | None, status: StepStatus, error: Any) -> None:
        try:
            self.recorder.end(step, status, error=error)
        except Exception:  # noqa: BLE001
            log.exception("trace: could not settle a tool step")

    def _settle(self, step: str | None, name: str, raw: dict, result: Any, deps: Any = None) -> None:
        try:
            text = _text_of(result)
            declared = self.tools.get(name)
            preview = refs = summary = error = None
            status = StepStatus.OK
            if declared is not None:
                try:
                    preview = declared.view_result(text)
                    summary = declared.call(declared.summary, raw, text, deps) if declared.summary else None
                    refs = list(declared.call(declared.refs, raw, text, deps)) if declared.refs else None
                    verdict = declared.call(declared.verdict, raw, text, deps) if declared.verdict else None
                    if verdict is not None:
                        status, error = verdict.status, error_of(verdict.code) if verdict.code else None
                except Exception:  # noqa: BLE001 - a bad declaration costs its detail, not the answer
                    log.exception("trace: the declared view of %s failed", name)
                    preview = summary = refs = error = None
                    status = StepStatus.OK
            elif self.recorder.level >= 3:
                preview = text
            self.recorder.end(step, status, error=error, summary=summary, result_text=text, preview=preview, refs=refs)
        except Exception:  # noqa: BLE001
            log.exception("trace: could not settle a tool step")


__all__ = ["TraceCapability"]
