"""The agent plane — pydantic-ai harness: tool loop, HITL, streaming.

`django_llm` has two planes, and the distinction is load-bearing:

| plane | what it does | depends on |
|---|---|---|
| **transport** (the package root) | one model call: chat, extract, embed, vision, image | OpenAI SDK |
| **agent** (here) | many model calls in a loop, with tools, approval and streaming | pydantic-ai + the transport |

The transport answers *"what does the model say?"*. The agent answers *"what does
the model DO?"* — it runs the tool loop, resolves human approval, streams events,
and accounts for the cost of a whole turn rather than a single call.

## Import this plane EXPLICITLY

```python
from django_cfg.modules.django_llm.agent import ...        # correct
from django_cfg.modules.django_llm import SomeAgentThing   # NEVER — see below
```

The package root must never re-export anything from here. Every Django app that
wants `embed_fast` imports the root; if the harness leaks into it, all of them pay
for pydantic-ai and the Monty sandbox at import time for a feature they do not use.
`tests/test_plane_isolation.py` enforces this — it is one line to break and
impossible to notice, so it is a test rather than a convention.

## Why one package and not two

A sibling `django_agent/` would need its own sync script, its own version skew
against the transport it depends on for provider keys, and would have to be released
in lockstep with it anyway. **Two packages that must ship together are one package.**
One package also means `sync_django_llm.sh` carries the harness into django-cfg for
free.

## What belongs here — and what does not

**Here (mechanism):** agent construction, the tool registry and `@llm_tool`
decorator, capabilities (lenient JSON args, per-turn call caps, history compaction,
the code-mode sandbox), streaming → SSE, message-history conversion, the deferred-tool
HITL flow, the anti-hallucination action guard, provider/model resolution.

**Not here (policy):** any tool that names a domain model, any prompt, any host's
tier map, any product copy. Those live in the host app and reach the harness through
the three Protocols below.

## The three seams

A host wires itself in through exactly three interfaces. **If a fourth appears, the
boundary is cut in the wrong place — stop and re-cut it.**

1. `AgentConfig`  — `resolve_primary(use_case)` / `resolve_fallbacks(use_case)`
2. `ToolProvider` — `get_tools()` / `get_toolsets()` (the provider closes over deps;
   `ActionGuardPolicy` hangs off `AgentDeps`, and is deliberately NOT a fourth seam)
3. `AgentDeps`    — the base deps a host subclasses to add its own context

Design and rationale live in the seam docstrings (`agent/protocols.py`) and
`@docs/agent/README.md`.
"""

from __future__ import annotations

__all__: list[str] = []
