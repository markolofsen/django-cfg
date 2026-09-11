---
title: General MCP Standard — index
status: current
version: "1.0"
audience: backend, ai, agents
last_reviewed: 2026-09-03
---

# `general/` — how to build an MCP surface

Rules that hold for **any** MCP server, not only this one. A page here must
survive being read in a project that shares none of this one's tools, models or
domain — so nothing here names `catalog`, `leads` or `operator`.

The half that does name them is [`../custom/`](../custom/README.md). The split
is the one [`@rules/`](../../../@rules/README.md) uses: a judgment you must
apply, kept apart from a fact you must look up. Mixing them is how a handbook
rots as one piece — a reader who finds a dead path stops trusting the paragraph
above it, which was fine.

| Page | Read it when |
|---|---|
| [01 — Talking to an agent](01-talking-to-an-agent.md) | Writing any tool, especially its description and its empty result |
| [02 — Bounds and arguments](02-bounds-and-arguments.md) | Deciding what a tool may return, or handling what a model actually sent |
| [03 — Package shape](03-package-shape.md) | Adding a tool group, splitting a file, or wondering where a helper goes |
| [04 — Security posture](04-security-posture.md) | Exposing anything — a model, a mutation, an anonymous surface |
| [05 — Verifying a tool](05-verifying-a-tool.md) | Before claiming a tool works |

## The four that keep recurring

Each of these cost a real defect in this codebase, and each generalises past
it.

**An agent cannot ask a follow-up question.** It gets one payload and reasons
from it, so anything the payload omits reads as absent *from the world* rather
than absent from the answer. That single fact drives most of 01 and 02.

**Registering is not working.** A tool can import cleanly, appear in
`tools/list`, and raise on every call. The only proof is calling it — see 05.

**A comment is not a mechanism.** Text saying a thing is grouped, retried or
bounded does nothing. If you cannot point at the line that enforces it, it is
not enforced.

**Correct is not the same as usable.** A tool that answers accurately in
490 000 characters has failed, because the answer never reaches the model that
asked. Measured here on 2026-09-03: five searches, none read. See 02.
