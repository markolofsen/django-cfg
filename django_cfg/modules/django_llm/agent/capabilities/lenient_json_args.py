"""Lenient JSON-string arg coercion capability.

A ``before_tool_validate`` hook that JSON-decodes any string args that
look like JSON arrays/objects. Cheap LLMs (Qwen/DeepSeek/Llama)
routinely send list/dict params as ``"[\\"x\\"]"`` instead of ``["x"]``;
pydantic ``ValidationError``s then exhaust ``retries`` and the run
aborts. Decoding upfront fixes this once for every tool.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic_ai import RunContext, ToolCallPart
from pydantic_ai.capabilities import Hooks
from pydantic_ai.tools import ToolDefinition

logger = logging.getLogger(__name__)


def _maybe_decode(value: Any) -> Any:
    """Best-effort JSON decode for a single arg value.

    Decodes only when the string clearly looks like a JSON literal
    (starts with ``[`` or ``{``). Plain strings like ``"urgent"`` are
    untouched so a ``str | list[str]`` union still resolves to ``str``.
    Recurses into lists/dicts in case nested arg objects also contain
    stringified inner arrays (rare but cheap to handle).
    """
    if isinstance(value, str):
        s = value.strip()
        if (s.startswith("[") and s.endswith("]")) or (
            s.startswith("{") and s.endswith("}")
        ):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return value
        return value
    if isinstance(value, list):
        return [_maybe_decode(v) for v in value]
    if isinstance(value, dict):
        return {k: _maybe_decode(v) for k, v in value.items()}
    return value


async def _coerce_json_strings(
    ctx: RunContext[Any],
    *,
    call: ToolCallPart,
    tool_def: ToolDefinition,
    args: Any,
) -> Any:
    """Decode stringified JSON arrays/objects inside tool args.

    ``args`` arrives as either:
      - ``str`` — full args blob, JSON-encoded by the model. We leave
        it alone; pydantic's ``validate_json`` already handles native
        nested types correctly when the *outer* envelope is a string.
      - ``dict`` — already-parsed kwargs. Per-field stringification
        is what bites us; rewrite each value via ``_maybe_decode``.
    """
    if not isinstance(args, dict):
        return args

    coerced: dict[str, Any] = {}
    rewrote = False
    for key, value in args.items():
        new_value = _maybe_decode(value)
        if new_value is not value:
            rewrote = True
        coerced[key] = new_value

    if rewrote:
        logger.info(
            "[capability] coerced JSON-string args for tool=%s",
            call.tool_name,
        )
    return coerced


def lenient_json_args_capability() -> Hooks[Any]:
    """Hooks capability that JSON-decodes stringified list/dict args.

    Attach to an ``Agent`` via ``capabilities=[lenient_json_args_capability()]``.
    No configuration needed — applies to every tool call.
    """
    hooks: Hooks[Any] = Hooks(before_tool_validate=_coerce_json_strings)
    return hooks
