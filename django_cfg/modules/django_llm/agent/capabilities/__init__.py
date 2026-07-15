"""Project-wide pydantic-ai capabilities.

Hooks-based extensions registered with every ``ChatAgent``. Each
capability solves one cross-cutting concern that we don't want to
sprinkle across 30+ tool definitions.

Currently provides:

- ``lenient_json_args_capability()`` — a ``before_tool_validate`` hook
  that JSON-decodes any string args that look like JSON arrays/objects.
  Cheap LLMs (Qwen/DeepSeek/Llama) routinely send list/dict params as
  ``"[\\"x\\"]"`` instead of ``["x"]``; pydantic ``ValidationError``s
  then exhaust ``retries`` and the run aborts. Decoding upfront fixes
  this once for every tool.

- ``intent_router_capability(history)`` — a ``prepare_tools`` hook
  that filters the ~30-tool admin surface down to ~5–10 tools
  matched to the user's latest message. Flash-class models drown in
  the full list and pattern-match the wrong tool; a smaller schema
  focuses the choice and is also cheaper (fewer tokens per turn).

Each concern lives in its own module:

- ``lenient_json_args`` — JSON-string arg coercion.
- ``intent_router`` — keyword → tool-bucket surface filtering.
- ``per_turn_call_cap`` — per-turn call-count guard.
"""

from __future__ import annotations

from .assembler import CapabilitySpec, build_capabilities
from .intent_router import intent_router_capability
from .lenient_json_args import lenient_json_args_capability
from .per_turn_call_cap import per_turn_call_cap_capability

__all__ = [
    "build_capabilities",
    "CapabilitySpec",
    "lenient_json_args_capability",
    "intent_router_capability",
    "per_turn_call_cap_capability",
]
