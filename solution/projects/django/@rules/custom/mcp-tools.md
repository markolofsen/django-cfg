---
title: MCP Tools
status: current
version: "2.0"
audience: backend, ai, security, operations, agents
last_reviewed: 2026-09-01
---

# MCP Tools

`django_cfg.modules.django_mcp` can expose introspection, ORM queries,
aggregations, user lookup, whitelisted management commands and custom tools
over MCP/JSON-RPC. **This is a privileged control surface.** Enable capabilities
deny-by-default; an access key alone is not product authorization.

The surface here is `mcp/` — 60 `.py` files, eight tool groups:
`payments`, `telemetry`, `frontend`, `referrals`, `crm`, `public_data`,
`analytics`, plus `_shared`. Configuration is `api/settings/builders/mcp.py`.

## Exposure policy

- **MUST**: expose only named models and fields required by a concrete operator
  workflow.
- **MUST**: read-only by default. A mutation tool calls a domain service, never
  a generic ORM update or delete.
- **MUST**: hide secrets, password/token/hash fields, personal data and
  internal security metadata explicitly — and verify the redaction with a test.
- **MUST**: apply tenant and object scope inside every tool, from authenticated
  context. See [`../general/security-and-tenancy.md`](../general/security-and-tenancy.md).
- **MUST**: cap rows, query complexity, time range, payload size and execution
  time.
- **MUST NOT**: expose arbitrary SQL, Python, shell, URL fetch, or unbounded
  management commands. Whitelist each command and validate its arguments; a
  destructive command needs separate confirmation.

Framework built-ins are **capabilities, not approval**. A generic `query_model`
or `get_user_info` may be unacceptable for a tenant-scoped external agent even
where field redaction exists.

At execution time, re-check actor, tenant, current state, idempotency and
business invariants. **The model cannot authorize its own tool call.**

Log tool name, a safe argument summary, actor/tenant reference, correlation ID,
duration and outcome — not secrets and not returned private rows.

**Untrusted tool output remains data and can carry prompt injection.** Do not
feed unbounded ORM dumps or command stdout into an LLM context.

## The package shape

Every tool group is a **package**, not a module. The convention, from
`mcp/tools/catalog/`, `mcp/tools/leads/` and `mcp/tools/operator/`:

```text
mcp/tools/<group>/
  __init__.py     the tool registrations
  _bounds.py      this group's ceilings — private
  _helpers.py     this group's shared query/formatting code — private
  <tool>.py       one file per tool
mcp/tools/_shared/
  arguments.py    reading caller arguments safely
  responses.py    how every tool speaks back
```

`mcp/tools/catalog/_bounds.py`, abridged — every constant there carries its
reasoning, which is the point:

```python
MAX_ROWS = 50          # under the REST API's 100: an agent reasons over what
DEFAULT_ROWS = 20      # it reads, and 100 full records is more than an answer needs
PUBLIC_MAX_ROWS = 25   # anonymous: no key to revoke, so the page is the unit of cost
MAX_QUERY_CHARS = 200  # matches the public API, so a query that works here works there
MAX_OFFSET = 10_000
```

**MUST**: put a group's ceilings in its own `_bounds.py`, as named constants
with the reasoning in the comment. A ceiling inlined at a call site is a
ceiling nobody can review, and a ceiling with no comment is one nobody dares
change.

**MUST NOT** hoist ceilings into `_shared/`. `_shared/arguments.py` states why:
*ceilings are passed in, never defaulted here — 100 rows of payments and 50
telemetry events are different costs, and a shared default would quietly become
the ceiling nobody chose.*

**SHOULD**: keep group-private helpers underscore-prefixed. Each group here
carries its own `_bounds.py` and `_helpers.py`; `catalog` and `leads` both do,
and neither reaches into the other's.

## Arguments arrive as whatever the model produced

`mcp/tools/_shared/arguments.py` — a string where an integer was declared, a
null, a missing key, an absurd limit are all **normal traffic, not misuse**.

**MUST**: clamp rather than raise. A tool that errors on `limit="25"` teaches
the agent that the tool is broken, and the agent stops using it — which is a
worse outcome than a clamped answer.

Use `clamp_limit(arguments, default=..., ceiling=...)` with the group's own
`_bounds` values rather than re-implementing the coercion.

## An empty result must be loud

This is the rule most worth carrying out of `mcp/`, and it generalises well
beyond this surface. From `mcp/tools/_shared/responses.py`:

> **An agent cannot ask a follow-up question.** It gets one payload and reasons
> from it, so anything the payload omits is treated as absent *from the world*
> rather than absent from the answer.
>
> A bare `[]` reads to an agent as "nothing is wrong" and ends the
> investigation. That is the wrong conclusion whenever the pipeline is broken
> rather than the subject idle — and this program has recorded four cases where
> an empty answer was written down as a fact about the product when it was a
> fact about the instrument.

**MUST**: return every empty result through `empty()`, which names three things:

| Key | Answers |
|---|---|
| `filters_applied` | what was actually asked — with empty values stripped, or `{"(none)": "unfiltered query"}` |
| `empty_reason` | why nothing came back |
| `hint` | what to try next |

The default hint states the distinction the caller has to make: *"Either the
filters are too narrow or there is no such data yet — these are different
situations; widen the filters to tell them apart."*

**SHOULD**: pass a specific `hint` whenever the group knows something the
generic text cannot. `hint` is optional rather than required only because the
two call styles it replaced disagreed; a specific one is worth far more —
payments' *"run `payments_webhook_health` before concluding nobody paid"* names
the next instrument, not just the next filter.

**MUST**: serialise through `dump()`. Its `default=str` is what lets datetimes,
UUIDs and `Decimal` through. Dropping it does not fail loudly — it raises deep
inside a tool call, where the agent sees a **transport error rather than an
answer**, and cannot tell the difference between "the tool is broken" and "the
data is bad".

## Protocol and keys

MCP endpoints need TLS, rate limits, request and body bounds, JSON-RPC
validation, key rotation and revocation, and environment-specific access.

**MUST NOT** share one static access key across unrelated clients or tenants.
Prefer a principal-bearing mechanism and map every request to explicit
permissions.

Introspection of URLs and schema reveals internal surfaces. **Disable it
outside trusted operator use** unless there is a documented need.

The optional MCP agent composes MCP tools with `django_llm`, so both the LLM
safety rules and the tool permission rules apply. It **MUST NOT** turn a
read-only MCP configuration into mutation through another capability.

## Testing

`mcp/tests/` exists; treat these as **security tests**, not happy-path protocol
tests. Cover: missing, invalid and revoked auth; cross-tenant access; hidden
fields; row and cost limits; malicious filters; prompt injection in returned
rows; command argument injection; timeouts; duplicate mutation; audit
redaction.

**SHOULD**: also test the empty path — that a no-match query returns
`filters_applied`, `empty_reason` and `hint`, not `[]`. That is the assertion
that would have caught four misread results.

## Review checklist

- Is the new tool read-only, or does it call a domain service for its mutation?
- Are this group's ceilings in its own `_bounds.py`, with the reasoning?
- Do arguments clamp rather than raise?
- Does every empty path go through `empty()` with a group-specific `hint`?
- Is tenant scope derived from authenticated context inside the tool?
- Are secrets and personal data explicitly excluded, with a test proving it?
- Could returned rows carry prompt injection into an LLM context unbounded?
