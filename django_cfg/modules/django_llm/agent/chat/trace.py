"""The tool trace of a stored answer, made safe for a client: `[{name, input, summary}]`, every part capped.

A stored call is `{id, name, input, output}` (the model's own view). A client gets the name, a trimmed copy of the
input and ONE short line about the outcome, written by the chat kind (`ChatKind.summarize_call`); never the raw output,
which may carry the whole document. Without a kind hook the summary is generic ("ok" / "no result" / "failed").
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

MAX_CALLS = 40  # calls shown per answer (a kind's tool_calls_limit is 24)
MAX_STR = 80  # characters of a string value kept in the input
MAX_ITEMS = 5  # items of a list / keys of an object kept in the input
MAX_DEPTH = 3
MAX_INPUT_CHARS = 800  # serialized, after trimming
MAX_SUMMARY = 160

Summarize = Callable[[str, dict, "str | None"], str]


def clip(text: str, limit: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def trim(value: Any, depth: int = 0) -> Any:
    """A bounded copy of a JSON value: long strings cut, long lists and objects shortened with a marker, deep nesting folded."""
    if isinstance(value, str):
        return clip(value, MAX_STR)
    if isinstance(value, dict):
        if depth >= MAX_DEPTH:
            return f"{{{len(value)} keys}}"
        out = {str(k)[:MAX_STR]: trim(v, depth + 1) for k, v in list(value.items())[:MAX_ITEMS]}
        if len(value) > MAX_ITEMS:
            out["…"] = f"{len(value) - MAX_ITEMS} more keys"
        return out
    if isinstance(value, list):
        if depth >= MAX_DEPTH:
            return f"[{len(value)} items]"
        out = [trim(v, depth + 1) for v in value[:MAX_ITEMS]]
        if len(value) > MAX_ITEMS:
            out.append(f"… {len(value) - MAX_ITEMS} more")
        return out
    return value if isinstance(value, (bool, int, float)) or value is None else clip(repr(value), MAX_STR)


def generic_summary(name: str, args: dict, output: str | None) -> str:
    if output is None:
        return "no result"
    return "failed" if output.startswith("error:") else "ok"


def compact(calls: Any, summarize: Summarize | None = None) -> list[dict]:
    """The wire form of a stored `tool_calls` list. Tolerates anything a row might hold: bad entries are skipped."""
    out: list[dict] = []
    for call in calls if isinstance(calls, list) else []:
        if not isinstance(call, dict) or not isinstance(call.get("name"), str):
            continue
        args = call.get("input") if isinstance(call.get("input"), dict) else {}
        output = call.get("output") if isinstance(call.get("output"), str) else None
        try:
            line = (summarize or generic_summary)(call["name"], args, output)
        except Exception:  # noqa: BLE001 - a summary is decoration; a bad one must not break the thread
            line = generic_summary(call["name"], args, output)
        shown = trim(args)
        if len(json.dumps(shown, ensure_ascii=False)) > MAX_INPUT_CHARS:
            shown = {"…": clip(json.dumps(shown, ensure_ascii=False), MAX_INPUT_CHARS)}
        out.append({"name": call["name"][:60], "input": shown, "summary": clip(line, MAX_SUMMARY)})
        if len(out) >= MAX_CALLS:
            break
    return out
