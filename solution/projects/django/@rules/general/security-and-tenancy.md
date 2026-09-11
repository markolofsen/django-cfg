---
title: Security and Tenancy
status: current
version: "2.0"
audience: backend, security, qa, agents
last_reviewed: 2026-09-01
---

# Security and Tenancy

Security is a property of the **complete request and side-effect path**, not a
decorator added to a view after its query is written. Which model is the tenant
boundary here, and which permission classes exist, is in
[`../custom/`](../custom/README.md).

## Tenant scope is derived, never accepted

Django provides no row-level security. Every tenant-owned query and mutation
therefore MUST derive its scope from **authenticated server-side identity**,
and MUST enforce it **before** object lookup, serialization, or enqueueing
work.

The ordering matters. Filtering after fetching means the object was already
loaded; filtering after serializing means it was already rendered; filtering
after enqueueing means a worker will act on it regardless of what the response
said.

**MUST NOT** treat any of these as authorization truth when they arrive from a
client: a tenant or organization ID, a role, an entitlement, an owner, a price,
a quantity, a plan, or a return URL. Each is a server-derived fact. A client may
*request*; only the server may *decide*.

**Least privilege, spelled out.** Distinguish an authenticated user, a member of
the tenant, a manager or owner, a staff operator, and a trusted internal caller.
An endpoint that only checks "is logged in" is an endpoint that any customer can
point at any other customer's data.

**Use the endpoint's intended mechanism.** An API-key route and an
internal-secret route each need their own authentication and permission
classes; inheriting the browser session's classes silently widens who can call
them.

## Do not leak existence

Return a safe response for a record the caller may not see, and avoid
diagnostic detail that reveals whether a resource exists or how the system is
laid out. A 404 that is really a 403 is usually the right answer; an error
message naming an internal service is not.

## Secrets

- **MUST NOT** put credentials in migrations, fixtures, generated clients,
  logs, request IDs, screenshots, error responses, or task arguments. Task
  arguments are the most-forgotten of those: they are persisted in the queue
  and often shown in a dashboard.
- Whether **dotenv files** are committed is a project-level decision, not a
  universal rule. A repository may deliberately commit them so a checkout is
  runnable and a rotation shows up in a diff. **Check the project's own
  configuration contract before "fixing" what looks like a leak** — and note
  that where this is the policy, rotating a key means reissuing it at the
  provider, not merely editing the file. The decision for this service is in
  [`../custom/`](../custom/README.md).
- **Redact before logging**: authorization headers, API keys, webhook
  signatures, payment secrets, and sensitive provider payloads.
- When comparing two credentials that should match, log a **length and a
  fingerprint** of each — never the values, and never a mask that hides the
  very difference you are trying to find.
- **Never rotate a credential to debug a mismatch.** Instrument the comparison
  point instead; rotating destroys the evidence and usually moves the failure
  rather than explaining it.

## The operator surface is not an exception

Restrict admin actions with the same care as API actions. **Admin convenience
is not authority to bypass a tenant or lifecycle rule** — an action that a
service refuses must not be reachable by a staff member clicking a button, or
the service's rule is decorative.

## Money and provider-owned state

Prices, customer identity, subscription state, invoices, usage and entitlements
are **server-owned**.

- A client may request a checkout. It may not choose the amount, mark a
  subscription active, or supply a return URL that changes a trust boundary.
- **An intermediate provider response is not success.** Final state becomes
  authoritative only through reconciliation of the provider-owned event.
- Free and paid flows have different semantics — do not let one inherit the
  other's assumptions by sharing a code path that was written for only one.
- Preserve idempotency around checkout, cancellation and webhooks, and **test
  the replay**, because replay is the case that happens in production and never
  in development.

## Review checklist

- Is tenant scope derived from server-side identity **before** any object is
  loaded, rendered, or enqueued?
- Does the endpoint use its intended auth mechanism, at least privilege?
- Is any client-supplied value being trusted as authorization or as a price?
- Are secrets absent from responses, logs, generated artifacts and task
  arguments?
- Does provider state become authoritative only after reconciliation?
