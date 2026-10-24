---
title: This Service — Index
status: current
version: "1.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# `custom/` — this service

The pages here name real things: apps, settings modules, queues, permission
classes, env flags, commands. They are the half of the handbook that would be
**false** — not merely irrelevant — in an unrelated Django project.

The routing rule is in [`../CLAUDE.md`](../CLAUDE.md). The short version:

- a rule about building Django services → [`../general/`](../general/README.md)
- a rule about the django-cfg framework → [`../djangocfg/README.md`](../djangocfg/README.md)
- a rule that names `apps.catalog`, `apps.normalizer`, the `normalization`
  queue or `api/settings/` → here

Where a rule is universal but its enforcement is local, the rule lives in
`general/` and the command lives here. "A job MUST be idempotent" is general.
"`make rq` derives its queue list from `settings.RQ_QUEUES`" is custom.

## Read by task

| You are about to… | Read |
|---|---|
| Find where a setting, app registration, queue or OpenAPI group is declared | [`settings-reference-profile.md`](./settings-reference-profile.md) |
| Locate the domain that owns a fact, or decide where a new one goes | [`app-roster-and-domains.md`](./app-roster-and-domains.md) |
| Verify a change before calling it done | [`gates-and-verification.md`](./gates-and-verification.md) |
| Run the suite, or work out why the test database will not drop | [`testing.md`](./testing.md) |
| Touch a catalogue model, write a migration, or see `DatabaseOperationForbidden` | [`two-databases.md`](./two-databases.md) |
| Add a plausibility rule, a normalizer validator, or a prompt fragment | [`ingestion-data-quality.md`](./ingestion-data-quality.md) |
| Add or change an environment variable, dotenv value, or Constance field | [`configuration-and-environment.md`](./configuration-and-environment.md) |
| Change a serializer, add an endpoint, or regenerate a client | [`api-groups-and-generation.md`](./api-groups-and-generation.md) |
| Add a queue, a schedule, or an enqueue site | [`background-work.md`](./background-work.md) |
| Write a service, an exception, a permission class, or money arithmetic | [`domain-conventions.md`](./domain-conventions.md) |
| Add a staff-only endpoint, or decide whether a field may be public | [`authorization-tiers.md`](./authorization-tiers.md) |
| Add or change an MCP tool | [`mcp-tools.md`](./mcp-tools.md) |

Read every page the table lists for your task, not the first. A new endpoint is
governed by the codegen page AND [`authorization-tiers.md`](./authorization-tiers.md)
AND [`../general/security-and-tenancy.md`](../general/security-and-tenancy.md) AND the
roster page; each owns a different half of the same edit.

The next hop after these pages is the **app's own `README.md`**. This directory
routes; it does not describe each domain.

## Keep the profile true

This directory ages faster than `general/`, because it names things that move.
The `api/config.py` path was named in 13 v1 pages after the file ceased to
exist; a `MUST NOT` keyed to a deleted module forbids nothing and reads as
though it does.

**MUST**: a number is a claim — carry the command that produced it. "20 apps"
is unverifiable; "20 apps (`ls apps/`, excluding `@archive`)" can be re-run by
the next reader in three seconds.

**MUST**: a correction to a false claim gets a visible retraction, not a silent
overwrite. A reader who learned the wrong fact needs to see it withdrawn;
otherwise they trust their memory over the page. Ordinary rewording needs no
note — reserve retractions for things that were untrue.

**SHOULD**: verify the neighbours while the file is open. If you are correcting
one queue name in a list of six, re-derive all six. A list corrected one entry
at a time stays wrong for longer than one corrected wholesale.

**AVOID**: describing a domain here that its own `README.md` already owns. Two
descriptions drift, and the one in this directory is the one nobody updates.

### The path check

Every backticked path in this directory must resolve, or sit inside a
retraction that names it as gone. Three lines, run from `projects/django`:

```python
import re
from pathlib import Path
P = re.compile(r'`((?:apps|api|mcp|modules)/[\w./-]+\.(?:py|md|json))`')
for p in Path("@rules/custom").glob("*.md"):
    for i, line in enumerate(p.read_text().splitlines(), 1):
        for m in P.findall(line):
            if not Path(m).exists():
                print(f"{p.name}:{i}: {m}")
```

Read every hit — a path inside a retraction is *correct* there, and the check
cannot tell the difference. On 2026-09-06 this found 24 broken paths across
nine pages; correcting them surfaced two live defects in the code the pages
described, which is the argument for running it rather than trusting the
prose.

## Review checklist

- Would this rule be **false**, not merely unused, in an unrelated Django
  project? If not, it belongs in `general/`.
- Does every path, command, count and setting name in the edit still exist —
  checked, not remembered?
- Does a corrected falsehood carry a visible retraction?
- Is the page routing to an app `README.md` rather than restating it?
- Is a new page registered in the table above in the same edit?
