---
title: MCP Surface Documentation
status: current
version: "2.0"
audience: backend, ai, operations, agents
last_reviewed: 2026-09-03
---

# MCP surface — documentation

Detail behind [`../README.md`](../README.md), which stays short on purpose.

```text
general/   how to build an MCP surface — true of any MCP server
custom/    this surface: its profiles, groups, tools and paths
```

**Start here:** [`general/README.md`](general/README.md) ·
[`custom/README.md`](custom/README.md) — each maps a task to its page.
How to read and change this directory: [`CLAUDE.md`](CLAUDE.md).

## Why two directories

The split separates **a judgment you must apply** from **a fact you must look
up**. It is the one [`@rules/`](../../@rules/README.md) uses, for the same
reason: mixing them is how a handbook rots as one piece. A reader who finds a
dead path stops trusting the paragraph above it, which was fine.

It also has a specific history here. Until 2026-09-03 this directory documented
a **different service** — tool groups (`payments`, `telemetry`, `analytics`,
`referrals`) that do not exist in this project, against a config shape this
project no longer has. Every page was individually plausible and collectively
false. The general half survived that; the custom half was the half that had
gone stale, and separating them is what makes the next drift visible instead of
invisible.

## Where to start

| You are… | Read |
|---|---|
| adding a tool | [`general/03`](general/03-package-shape.md), then [`custom/02`](custom/02-tool-groups.md) |
| writing a tool's description or its empty result | [`general/01`](general/01-talking-to-an-agent.md) |
| deciding what it may return | [`general/02`](general/02-bounds-and-arguments.md) |
| exposing anything at all | [`general/04`](general/04-security-posture.md), then [`custom/01`](custom/01-configuration-and-profiles.md) |
| reading a result and unsure what it means | [`custom/03`](custom/03-tool-reference.md) |
| connecting a client | [`custom/04`](custom/04-connecting-a-client.md) |
| about to say it works | [`general/05`](general/05-verifying-a-tool.md) |

## Four things that recur, each paid for

- **An agent cannot ask a follow-up question.** One payload, no clarification.
  Everything it omits reads as absent from the world.
- **Registering is not working.** A tool imported cleanly, listed, and raised
  on every call for its whole life.
- **A comment is not a mechanism.** Grouping that "can retry" and never does; a
  rate limit validated, stored and enforced nowhere.
- **Correct is not usable.** Five searches answered accurately in 168k–490k
  characters each; none reached the model that asked.

**The config is not in this directory's parent.** It is
[`../../api/settings/mcp_config.py`](../../api/settings/mcp_config.py), moved
there on 2026-08-18 because two declarations existed and the loader silently
kept the wrong one. `mcp/` holds tools. A page pointing at `mcp/__init__.py` is
stale — fix it.
