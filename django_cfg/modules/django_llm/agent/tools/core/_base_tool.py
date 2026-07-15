"""BaseTool — typed, hookable tool framework.

Tools inherit from ``BaseTool``, override ``run()``, and optionally hook into
``before_call`` / ``after_call`` / ``on_error``.

A tool reaches the agent by being named in ``ai/tools/registry.py``
(``get_tools_for_deps``), or — for host projects — by being registered with
``tier_tool_registry`` / ``project_tool_registry``. There is no auto-discovery:
the old ``ToolRegistry`` collected 82 ``@register`` decorations into a dict that
nothing outside itself ever read, so it was removed.
"""

from __future__ import annotations

import contextvars
import functools
import inspect
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Generic, TypeVar

# Sentinel embedded in the tool return string to carry structured data
# back to streaming.py without relying on ContextVar (which doesn't
# propagate from asyncio.to_thread back to the async caller).
_RAW_SENTINEL = "\x00RAW\x00"

# Legacy ContextVar kept for backward-compat imports in tests.
_tool_raw_results: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "_tool_raw_results", default={}
)


def _embed_raw(llm_text: str, raw: Any) -> str:
    """Append raw JSON payload to llm_text using sentinel separator."""
    return llm_text + _RAW_SENTINEL + json.dumps(raw, separators=(",", ":"), default=str)


def strip_raw(text: str) -> tuple[str, Any]:
    """Split sentinel-encoded string into (llm_text, raw_data | None)."""
    idx = text.find(_RAW_SENTINEL)
    if idx == -1:
        return text, None
    llm_text = text[:idx]
    try:
        raw = json.loads(text[idx + len(_RAW_SENTINEL):])
    except Exception:
        raw = None
    return llm_text, raw

from pydantic import BaseModel
from pydantic_ai import RunContext

from ._meta import ToolMeta, attach_meta, attach_sandbox_callable, get_tool_meta
from ._serialize import serialize_for_llm
from .schemas.base import ToolError, ToolErrorException

logger = logging.getLogger(__name__)

TDeps = TypeVar("TDeps")


@dataclass
class ToolExecution:
    """Internal return shape of ``BaseTool._execute()``.

    Three independent surfaces flow out of a tool run, each consumed by
    a different downstream:

    - ``llm_text`` — compact string fed back into the model's context.
      pydantic-ai sees this (via ``as_callable``) as the function-tool
      return; the LLM reads it.
    - ``raw_data`` — structured dict / list shipped to the frontend as
      ``ToolResultEvent.data`` for the legacy debug surface. ``None``
      on tool errors. See ``_embed_raw`` / ``strip_raw`` for the
      cross-thread plumbing (the sentinel-in-string trick).
    - ``ui_payload`` — typed Pydantic model (from
      ``apps/crm/apps/chat/agent/runtime/ui_payloads.py``) that drives
      a frontend widget (vehicle cards, tax breakdown, …). Rides
      ``ToolReturnPart.metadata`` per pydantic-ai's UI-adapter
      convention. ``None`` for tools that don't drive widgets.

    Lived as a 2-tuple originally; promoted to a dataclass so adding
    future channels doesn't ripple through every override site.
    """

    llm_text: str
    raw_data: Any = None
    ui_payload: Any = None


class BaseTool(ABC, Generic[TDeps]):
    """Abstract base for all LLM tools.

    Subclass overrides:
      - ``name``          (str) — defaults to snake_case class name
      - ``description``   (str) — docstring used as fallback
      - ``meta``          (ToolMeta) — category, visibility, approval
      - ``result_schema`` (type[BaseModel]) — pydantic model for success
      - ``enabled``       (bool) — static toggle; ``False`` skips registration

    Hooks (optional overrides):
      - ``before_call(ctx, **kwargs) -> dict`` — mutate/validate args
      - ``after_call(ctx, result, duration_ms) -> Any`` — metrics, side effects
      - ``on_error(ctx, exc) -> ToolError`` — custom error formatting

    The ``__call__`` wrapper serialises the result for the LLM,
    catches exceptions, and enforces ``result_schema`` / ``ToolError``.
    """

    name: ClassVar[str] = ""
    meta: ClassVar[ToolMeta] = ToolMeta(category="read")
    result_schema: ClassVar[type[BaseModel] | None] = None
    enabled: ClassVar[bool] = True

    def __init__(self, deps: TDeps | None = None) -> None:
        self.deps = deps

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Auto-name from class if not explicitly set
        if not cls.name:
            cls.name = cls._default_name()
        # Auto-description from docstring
        if not getattr(cls, "description", None):
            cls.description = (cls.__doc__ or "").strip()

    @classmethod
    def _default_name(cls) -> str:
        """Convert ``LinkClientsTool`` → ``link_clients``."""
        name = cls.__name__
        if name.endswith("Tool"):
            name = name[:-4]
        # CamelCase → snake_case
        result: list[str] = []
        for i, ch in enumerate(name):
            if ch.isupper() and i > 0 and name[i - 1].islower():
                result.append("_")
            result.append(ch.lower())
        return "".join(result)

    # ------------------------------------------------------------------
    # Hooks (no-op defaults)
    # ------------------------------------------------------------------

    def before_call(
        self, ctx: RunContext[TDeps], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Mutate or validate kwargs before ``run()``.

        Return the (possibly updated) kwargs dict. Raising here aborts
        the call and routes through ``on_error``.

        No-op by default. Subclasses that override this hook (typically
        for an auth gate) do **not** need to re-implement unknown-kwarg
        filtering: the framework runs ``_filter_kwargs`` after this hook
        unconditionally, so a hallucinated argument can never reach
        ``run()`` regardless of what an override returns.
        """
        return kwargs

    def after_call(
        self,
        ctx: RunContext[TDeps],
        result: Any,
        duration_ms: float,
    ) -> Any:
        """Post-process result. Return possibly modified result."""
        return result

    def on_error(
        self, ctx: RunContext[TDeps], exc: Exception
    ) -> ToolError:
        """Format exception into ``ToolError``."""
        return ToolError(error=f"{self.name} crashed", detail=str(exc))

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    @abstractmethod
    def run(self, ctx: RunContext[TDeps], **kwargs: Any) -> Any:
        """Tool body. Must return ``result_schema`` instance or ``ToolError``."""
        ...

    def result_ui_payload(
        self, ctx: RunContext[TDeps], result: Any
    ) -> Any:
        """Optional hook — return a UI payload (pydantic model from
        ``apps/crm/apps/chat/agent/runtime/ui_payloads.py``) for the
        frontend to render a widget after this tool runs.

        Default: ``None`` — tool has no widget. Subclasses that drive
        UI surfaces (vehicle cards, tax breakdown chips, …) override.

        Called only when the tool succeeded (``result`` is a
        ``result_schema`` instance, not a ``ToolError``). The payload
        rides ``ToolReturnPart.metadata`` via ``as_callable`` — the
        LLM never sees it, the streaming runtime drains it as a
        ``UIPayloadEvent``.
        """
        return None

    def _filter_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Drop kwargs that ``run()`` does not declare.

        The LLM-facing JSON schema is generated from ``run()``'s typed
        signature (see ``as_callable``), so a well-behaved model only
        passes declared arguments. Models still occasionally emit a
        stray one — silently dropping it here, as a framework guarantee
        applied right after ``before_call``, keeps it from crashing
        ``run()`` with a ``TypeError``. No-op when ``run()`` accepts
        ``**kwargs`` (VAR_KEYWORD).
        """
        sig = inspect.signature(self.run)
        if any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        ):
            return kwargs
        known = set(sig.parameters) - {"self", "ctx"}
        unknown = set(kwargs) - known
        if unknown:
            logger.debug(
                "[mcp-tool] %s: dropping unknown kwargs %s", self.name, unknown
            )
        return {k: v for k, v in kwargs.items() if k in known}

    def _execute(self, ctx: RunContext[TDeps], **kwargs: Any) -> ToolExecution:
        """Run the tool and return a ``ToolExecution`` carrying every
        downstream surface — see the dataclass docstring for fields.
        """
        t0 = time.monotonic()
        try:
            kwargs = self.before_call(ctx, kwargs)
            kwargs = self._filter_kwargs(kwargs)
            result = self.run(ctx, **kwargs)
        except ToolErrorException as exc:
            result = exc.tool_error
        except Exception as exc:
            logger.exception("[mcp-tool] %s raised", self.name)
            result = self.on_error(ctx, exc)

        elapsed = (time.monotonic() - t0) * 1000
        result = self.after_call(ctx, result, elapsed)

        err_cls = ToolError
        schemas: tuple[type[BaseModel], ...] = ()
        if self.result_schema is not None:
            schemas = (self.result_schema,)

        if isinstance(result, err_cls):
            return ToolExecution(
                llm_text=serialize_for_llm(result.model_dump(mode="json"), prefer="json"),
            )
        if schemas and isinstance(result, schemas):
            raw = result.model_dump(mode="json")
            # Pull a UI payload from the success result if the tool
            # opts in via the ``result_ui_payload`` hook. Errors here
            # are non-fatal — a missing widget is preferred over a
            # broken response.
            ui_payload: Any = None
            try:
                ui_payload = self.result_ui_payload(ctx, result)
            except Exception:
                logger.exception(
                    "[mcp-tool] %s.result_ui_payload raised — skipping widget",
                    self.name,
                )
            return ToolExecution(
                llm_text=serialize_for_llm(raw, prefer="auto"),
                raw_data=raw,
                ui_payload=ui_payload,
            )

        logger.error(
            "[mcp-tool] %s returned %s; expected %s | %s",
            self.name,
            type(result).__name__,
            " | ".join(s.__name__ for s in schemas) if schemas else "—",
            err_cls.__name__,
        )
        err = err_cls(
            error="internal error",
            detail=f"{self.name} returned unexpected type {type(result).__name__}",
        )
        return ToolExecution(
            llm_text=serialize_for_llm(err.model_dump(mode="json"), prefer="json"),
        )

    def _call(self, ctx: RunContext[TDeps], **kwargs: Any) -> str:
        """pydantic-ai entry point — returns only the LLM-facing string."""
        return self._execute(ctx, **kwargs).llm_text

    def __call__(self, ctx: RunContext[TDeps], **kwargs: Any) -> str:
        """Synchronous entry point — pydantic-ai calls this."""
        return self._call(ctx, **kwargs)

    # ------------------------------------------------------------------
    # Compatibility with existing @llm_tool functions
    # ------------------------------------------------------------------

    def _run_with_hooks(self, ctx: RunContext[TDeps], **kwargs: Any) -> Any:
        """Run ``before_call`` + ``run`` and return the raw result.

        Used as ``__wrapped__`` so tests that bypass the serializer
        still exercise auth gates.
        """
        try:
            kwargs = self.before_call(ctx, kwargs)
            kwargs = self._filter_kwargs(kwargs)
            return self.run(ctx, **kwargs)
        except ToolErrorException as exc:
            return exc.tool_error

    def as_callable(self) -> Callable[..., Any]:
        """Return a plain callable that pydantic-ai can use as a function tool.

        Two side channels coexist here, both flowing back to streaming.py:

        1. ``raw_data`` — structured JSON for the **legacy** ``tool_result``
           SSE event. Embedded in the return string with ``_RAW_SENTINEL``
           because pydantic-ai calls sync tools via ``asyncio.to_thread``
           and ContextVar mutations inside the thread are not visible to
           the async caller — the sentinel-in-string approach is the only
           reliable cross-thread channel for this content. ``streaming.py``
           runs ``strip_raw()`` on the tool result text, splits off the
           hidden payload, and attaches it as ``ToolResultEvent.data``.

        2. ``ui_payload`` — typed Pydantic model for the
           ``ui_payload`` SSE event. Riding on ``ToolReturnPart.metadata``
           per pydantic-ai's own UI-adapter convention
           (``ui/vercel_ai/_utils.py:iter_metadata_chunks``). Tools opt
           in by overriding ``result_ui_payload``. The LLM never sees
           ``metadata``; ``streaming.py`` drains it and emits the
           side-channel event independently of the tool-event gate.

        When neither side channel is populated we return a plain string —
        equivalent to the original behaviour and lighter than wrapping
        every tool's return in a ``ToolReturn`` instance.
        """
        tool_name = self.name

        def _wrapper(ctx: RunContext[TDeps], **kwargs: Any) -> Any:
            execution = self._execute(ctx, **kwargs)
            payload_str = (
                _embed_raw(execution.llm_text, execution.raw_data)
                if execution.raw_data is not None
                else execution.llm_text
            )
            if execution.ui_payload is not None:
                # ToolReturn lets us attach metadata that the streaming
                # runtime reads (see ToolReturnPart.metadata convention
                # in pydantic-ai). Imported lazily so importing the tool
                # module doesn't force a hard pydantic-ai dependency at
                # module load time on hosts that don't run agents.
                from pydantic_ai import ToolReturn
                return ToolReturn(return_value=payload_str, metadata=execution.ui_payload)
            return payload_str

        functools.update_wrapper(_wrapper, self._run_with_hooks)
        _wrapper.__name__ = tool_name  # type: ignore[attr-defined]
        _wrapper.__qualname__ = tool_name  # type: ignore[attr-defined]

        # ``update_wrapper`` copied ``_run_with_hooks``' metadata onto the
        # wrapper — ``__wrapped__`` (kept on purpose: tests call it to
        # exercise auth gates directly), plus ``__doc__`` and
        # ``__annotations__``. pydantic-ai derives the LLM-facing tool
        # schema from ``inspect.signature()`` + ``get_type_hints()`` +
        # the docstring, and ``inspect.signature`` follows ``__wrapped__``
        # down to ``_run_with_hooks``, whose ``(ctx, **kwargs)`` signature
        # collapses the JSON schema to ``{additionalProperties: true}``.
        # The model is then left to *guess* argument names, and every
        # call fails with ``TypeError: run() got an unexpected keyword
        # argument``. Re-point all three schema inputs at the real
        # ``run()`` so the model sees its true, typed parameters.
        # (``__signature__`` makes ``inspect.signature`` stop unwrapping
        # here, so ``__wrapped__`` stays available for tests.)
        try:
            run_sig = inspect.signature(self.run, eval_str=True)
        except Exception:
            logger.exception(
                "[mcp-tool] %s: could not resolve run() signature — "
                "LLM schema stays permissive", self.name,
            )
        else:
            _wrapper.__signature__ = run_sig  # type: ignore[attr-defined]
            annotations = {
                name: p.annotation
                for name, p in run_sig.parameters.items()
                if p.annotation is not inspect.Parameter.empty
            }
            if run_sig.return_annotation is not inspect.Signature.empty:
                annotations["return"] = run_sig.return_annotation
            _wrapper.__annotations__ = annotations
        _wrapper.__doc__ = self.description or (self.run.__doc__ or "")

        attach_meta(_wrapper, self.meta)
        # Tool modules export the callable, not the instance
        # (``list_tasks = ListTasksTool().as_callable()``), so carry the sandbox
        # projection along with it — otherwise ``CodeMode`` has no way back to the
        # ``BaseTool`` that can produce it. See ``attach_sandbox_callable``.
        attach_sandbox_callable(_wrapper, self.as_sandbox_callable())
        return _wrapper

    def as_sandbox_callable(self) -> Callable[..., Any]:
        """Return a callable for ``CodeMode``, which hands the value to model-written Python.

        ``as_callable`` is built for a **native** tool call: it returns
        ``llm_text`` — prose for the model to read — with ``raw_data`` glued on
        behind ``_RAW_SENTINEL`` and ``ui_payload`` riding ``ToolReturn.metadata``.
        ``streaming.py`` pulls those apart again.

        Inside a sandbox that shape is not merely unhelpful, it is unusable.
        ``CodeMode`` passes the return value straight into the model's Python, so

            tasks = await list_tasks(status='todo')
            [t for t in tasks if t['is_overdue']]

        would be indexing a ``str`` and dies with ``TypeError: str indices must
        be integers``. Worse, ``CodeMode`` renders the *declared return type* into
        the function catalog it shows the model, so a tool annotated ``-> str``
        teaches the model to write string-handling code and it never attempts the
        loop the sandbox exists to run.

        So this projection returns ``execution.raw_data`` — the structured surface
        ``ToolExecution`` has always carried — and keeps ``run()``'s real return
        annotation. The two side channels are deliberately dropped:

        - ``ui_payload`` drives a frontend widget, and code running in a loop has
          no single result to render a widget from.
        - the ``raw_data`` sentinel is redundant here: the data *is* the return.

        Native calls keep using ``as_callable`` untouched, so the SSE contract and
        the UI widgets do not move.

        A tool whose ``raw_data`` is ``None`` — in practice a ``ToolError``, since
        ``_execute`` rejects any return that is neither ``result_schema`` nor
        ``ToolError`` — falls back to ``llm_text``. That keeps the failure legible
        to model code rather than handing it a bare ``None`` it would read as an
        empty result and keep looping over.
        """
        tool_name = self.name

        def _wrapper(ctx: RunContext[TDeps], **kwargs: Any) -> Any:
            execution = self._execute(ctx, **kwargs)
            if execution.raw_data is not None:
                return execution.raw_data
            # A failure. **Raise, do not return a ToolError.**
            #
            # Returning it makes the sandbox signature ``Result | ToolError``, and
            # Monty type-checks the model's code against that union *before* running
            # it: ``res['rows']`` is then rejected with ``Unknown key "rows" for
            # TypedDict ToolError``. The model has three retries to guess the
            # narrowing idiom, and it often does not — so the same scenario passed or
            # failed at random depending on whether it got there in time. The flake
            # was this union.
            #
            # Raising keeps the sandbox signature clean (``-> ListTasksResult``), so
            # ``res['rows']`` type-checks on the first attempt. Model code that wants
            # to handle a failure still can — Monty propagates an external function's
            # exception into the sandbox as an ordinary Python exception, catchable
            # with ``try/except``. Code that does not handle it fails with a legible
            # message instead of silently indexing an error dict.
            raise ToolErrorException(
                ToolError(
                    error=execution.llm_text or f"{tool_name} failed",
                    detail="",
                )
            )

        functools.update_wrapper(_wrapper, self._run_with_hooks)
        _wrapper.__name__ = tool_name  # type: ignore[attr-defined]
        _wrapper.__qualname__ = tool_name  # type: ignore[attr-defined]

        # Same reasoning as ``as_callable``: ``update_wrapper`` leaves
        # ``__wrapped__`` pointing at ``_run_with_hooks``, whose ``(ctx, **kwargs)``
        # signature would collapse the rendered function signature to ``**kwargs``
        # and leave the model guessing argument names. Re-point at ``run()`` so the
        # sandbox catalog shows the true, typed parameters — and the true return
        # type, which is what tells the model it may iterate the result.
        #
        # ``ctx`` stays in the signature. pydantic-ai infers ``takes_ctx`` from the
        # first parameter's annotation being a ``RunContext`` and injects it, while
        # already excluding it from the JSON schema the model sees — the framework
        # separates those two concerns for us. Stripping it here breaks the
        # inference, and the tool then raises ``missing 1 required positional
        # argument: 'ctx'`` the moment the sandbox calls it.
        try:
            run_sig = inspect.signature(self.run, eval_str=True)
        except Exception:
            logger.exception(
                "[mcp-tool] %s: could not resolve run() signature — "
                "sandbox catalog stays permissive", self.name,
            )
        else:
            # The return type the *sandbox catalog* advertises is the success type
            # alone, not ``run()``'s ``Result | ToolError`` union. The wrapper above
            # raises on failure rather than returning the error, so the union is not
            # true here — and advertising it is actively harmful: Monty type-checks
            # the model's code against the signature *before running it*, and on the
            # ``ToolError`` arm ``res['rows']`` is rejected with ``Unknown key
            # "rows"``. Three retries to guess the narrowing idiom, and the scenario
            # passed or failed depending on whether the model got there in time. That
            # was the flake.
            #
            # Both ``__signature__`` and ``__annotations__`` carry it: pydantic-ai
            # builds the ToolDefinition's return schema from one and
            # ``inspect.signature`` reads the other.
            if self.result_schema is not None:
                run_sig = run_sig.replace(return_annotation=self.result_schema)

            _wrapper.__signature__ = run_sig  # type: ignore[attr-defined]
            annotations = {
                name: p.annotation
                for name, p in run_sig.parameters.items()
                if p.annotation is not inspect.Parameter.empty
            }
            if run_sig.return_annotation is not inspect.Signature.empty:
                annotations["return"] = run_sig.return_annotation
            _wrapper.__annotations__ = annotations
        _wrapper.__doc__ = self.description or (self.run.__doc__ or "")

        attach_meta(_wrapper, self.meta)
        return _wrapper


__all__ = ["BaseTool"]
