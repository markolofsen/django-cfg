---
title: Services, Errors, and Integrations
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# Services, Errors, and Integrations

A service is a **domain boundary with a meaningful operation**, not a folder
for every function that did not fit in a view.

## When to introduce a service

Use one for multi-model state transitions, authorization-aware domain queries,
pricing or entitlement decisions, provider calls, and workflows shared by HTTP,
admin, commands, or jobs. Keep simple model CRUD and one-off output formatting
in their natural layer.

A public service method makes its contract obvious:

- typed inputs or a validated DTO;
- **one** named domain operation;
- an explicit transaction and side-effect boundary;
- a model, typed result object, or documented result shape;
- expected domain exceptions, distinct from unexpected defects.

**AVOID**: a generic `utils.py`; service methods coupled to the HTTP
request/response objects; raw provider dictionaries flowing through the domain.
Normalize an external payload at the integration boundary, and retain the raw
payload only when audit or replay genuinely requires it.

A service coupled to a request object cannot be called by a job, a command, or
the admin — which is exactly the reuse the service existed to provide.

## Error ownership

| Layer | Responsibility |
|---|---|
| Provider / transport | timeout, protocol, authentication, malformed response |
| Service / domain | invalid transition, conflict, unavailable capability |
| API / admin / task | map expected errors to its surface and recovery behavior |
| Observability | retain redacted diagnostic cause and correlation context |

**MUST NOT** catch `Exception` merely to continue with invented fallback data.
Catch the narrow failure you can handle, preserve causal chaining
(`raise … from err`), and let unexpected defects reach the configured error
boundary.

**A fallback is acceptable only when the domain defines it, and only when the
degraded result is honest.** A default that is indistinguishable from a real
answer converts an outage into wrong data, which is strictly worse: the outage
would have been noticed.

**Define domain exceptions where a caller must tell failures apart.** A caller
forced to inspect an error message is a caller that breaks on a reworded
string. Where a domain has no exception module at all, every failure arrives as
a generic error and every caller guesses.

## Provider clients

- **Centralize base URL, credentials, timeouts, retries and response parsing in
  the integration owner.** A caller that constructs a second client with
  different policy has forked the timeout and retry behaviour invisibly.
- **Set finite connect, read and total timeouts.** A missing timeout is an
  unbounded wait that will eventually hold a worker, a connection, or a lock.
- Retry only transient, idempotent work; apply backoff; respect rate limits.
- **Use provider idempotency keys for monetary or creation operations**, and
  reuse the same key for a retry of the same intent. A new key per retry is not
  idempotency — it is a second charge.
- **MUST NOT** log tokens, signatures, full sensitive payloads, or unredacted
  provider errors. Attach stable internal identifiers for diagnosis instead.
- Project provider-specific states into stable domain vocabulary unless the
  product contract genuinely needs the raw one; retain the raw detail for
  operators.

## Every entry point shares the transition

HTTP, admin, management commands, scheduled jobs and webhooks **MUST call the
same service for the same transition.** Their authentication, acknowledgement
and presentation differ; the business invariant does not.

When a transition is implemented twice — once in a view and once in an admin
action — the two will diverge, and the one with fewer callers will be the one
nobody notices is wrong.

## Review checklist

- Is the service a real domain seam, or displaced view logic?
- Can it be called without an HTTP request object?
- Are provider types and failures normalized exactly once?
- Are timeout, retry, idempotency and redaction policies explicit?
- Does any `except` continue with invented data rather than failing honestly?
- Do all entry points reuse the same transition rules?
