---
title: This MCP Surface — index
status: current
version: "1.0"
audience: backend, ai, operations, agents
last_reviewed: 2026-09-03
---

# `custom/` — this MCP surface

The pages here name real things: tool names, groups, settings modules, mount
paths, env flags. They are the half of this documentation that would be
**false** — not merely irrelevant — in another project.

The half that travels is [`../general/`](../general/README.md).

| Page | Read it when |
|---|---|
| [01 — Configuration and profiles](01-configuration-and-profiles.md) | Changing what is exposed, to whom, or on which path |
| [02 — The tool groups](02-tool-groups.md) | Adding a tool, or deciding which group it belongs to |
| [03 — Tool reference](03-tool-reference.md) | Reading a result and wanting to be sure what it means |
| [04 — Connecting a client](04-connecting-a-client.md) | Registering the server with Claude Code or Codex |

## What this surface is

Two profiles over **15 tools in three groups**, served by one process.

| Profile | Path | Auth | Tools |
|---|---|---|---|
| operator | `/cfg/mcp/` | `X-MCP-Access-Key` | all 15 + django-cfg built-ins |
| public | `/mcp/` | none | the 4 `catalog_*` tools |

The public profile is also reachable at
`https://mcp.caribbeanrealestatemls.com/mcp/`.

```text
tools/
  catalog/    4 tools — the published catalogue, the only public group
  leads/      5 tools — inbound concierge briefs
  operator/   6 tools — the catalogue as a control surface, incl. mutations
  _shared/    argument coercion and the response shapes
```

## Three facts worth knowing before you change anything

**The config is not in `mcp/`.** It lives in
[`../../api/settings/mcp_config.py`](../../../api/settings/mcp_config.py). It
moved there on 2026-08-18 because two declarations existed and the auto-loader
silently kept the wrong one — while the committed key was the one winning at
runtime. `mcp/` holds tools only. A page pointing at `mcp/__init__.py` is
stale.

**A group registers nothing without its shim.** django-cfg globs
`mcp/tools/*.py`, flat and non-recursive, so `catalog/` is invisible to
discovery on its own; `catalog_tools.py` is what registers it. Delete the shim
and the tools vanish from `tools/list` with no error — see
[02](02-tool-groups.md).

**Public means the tool says so.** A tool carries `public = True`, and the
anonymous profile is built from that declaration rather than from a list in
settings. A list would drift the day someone adds a tool.
