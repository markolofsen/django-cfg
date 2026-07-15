"""@llm_tool — validate + serialise the return value of an MCP tool.

The wrapped function returns a typed Pydantic object (the
``result_schema``) on success, or a ``ToolError`` on failure. The
decorator handles both:

- ``result_schema`` instance → ``serialize_for_llm`` with the tool's
  preferred format (``toon`` / ``json`` / ``auto``);
- ``ToolError`` instance → always JSON (errors are envelopes, never
  tabular);
- exception or wrong type → log + return a generic JSON error to the
  agent. The agent learns a tool failed; the operator gets the trace
  in logs.

Internal callers can still get the typed object via
``tool.__wrapped__(ctx, ...)`` (functools.wraps preserves it).
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, Literal

from pydantic import BaseModel

from ._meta import ToolMeta, attach_meta
from ._serialize import serialize_for_llm
from .schemas.base import ToolError


logger = logging.getLogger(__name__)

Prefer = Literal["toon", "json", "auto"]


def llm_tool(
    *,
    result_schema: type[BaseModel] | tuple[type[BaseModel], ...],
    error_schema: type[BaseModel] | None = None,
    prefer: Prefer = "auto",
    meta: ToolMeta | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    """Decorator factory for MCP tools.

    Args:
        result_schema: Pydantic model the tool returns on success.
            Pass a tuple of models when the tool returns one of
            several shapes (e.g. ``confirm_send`` returns either
            ``ConfirmSendResult`` for single sends or
            ``BatchConfirmResult`` for batch sends).
        error_schema: Pydantic model the tool returns on validated
            failure. Defaults to ``ToolError``.
        prefer: Serialisation hint for the success path. Errors are
            always JSON.
        meta: Policy tags (``ToolMeta``). The rubric composer reads
            these to decide which policy text to inject into the
            system prompt. Optional but strongly recommended — without
            meta a tool is invisible to rubric composition, which is
            usually a bug.
    """
    err_cls = error_schema or ToolError
    result_schemas: tuple[type[BaseModel], ...] = (
        result_schema if isinstance(result_schema, tuple) else (result_schema,)
    )

    timeout_s = meta.resolved_timeout() if meta is not None else 10.0

    def decorate(fn: Callable[..., Any]) -> Callable[..., str]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> str:
            t0 = time.monotonic()
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                # Tools should validate their inputs and return ToolError
                # on user-visible failures. An exception here means a
                # bug — surface a generic message to the LLM, full
                # traceback to logs.
                logger.exception("[mcp-tool] %s raised", fn.__name__)
                return serialize_for_llm(
                    err_cls(
                        error=f"{fn.__name__} crashed",
                        detail=str(exc),
                    ).model_dump(mode="json"),
                    prefer="json",
                )

            elapsed = time.monotonic() - t0
            if elapsed > timeout_s:
                # Soft warning: a hard kill would need a separate
                # thread/signal infra that breaks Django's per-test
                # transaction isolation. We log the over-budget call so
                # operators can spot consistently slow tools and either
                # tighten the query or raise the budget. Hard timeouts land
                # with the pydantic-ai HITL path — DeferredToolRequests
                # naturally interrupts a hanging tool by ending the run.
                logger.warning(
                    "[mcp-tool] %s slow: %.2fs > budget %.1fs",
                    fn.__name__, elapsed, timeout_s,
                )

            if isinstance(result, err_cls):
                return serialize_for_llm(
                    result.model_dump(mode="json"), prefer="json",
                )
            if isinstance(result, result_schemas):
                return serialize_for_llm(
                    result.model_dump(mode="json"), prefer=prefer,
                )

            schema_names = " | ".join(s.__name__ for s in result_schemas)
            logger.error(
                "[mcp-tool] %s returned %s; expected %s | %s",
                fn.__name__,
                type(result).__name__,
                schema_names,
                err_cls.__name__,
            )
            return serialize_for_llm(
                err_cls(
                    error="internal error",
                    detail=f"{fn.__name__} returned unexpected type "
                           f"{type(result).__name__}",
                ).model_dump(mode="json"),
                prefer="json",
            )

        if meta is not None:
            attach_meta(wrapper, meta)
        return wrapper

    return decorate
