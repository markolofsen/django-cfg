---
title: Architecture and Ownership
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# Architecture and Ownership

Architecture exists to make a domain change **local and auditable**. One fact
has one canonical owner; consumers use a public contract or derive a
projection. Which apps exist here and where the registry lives is in
[`../custom/`](../custom/README.md).

## The layers, and what each one owns

Django gives you five places to put a decision. Putting it in the wrong one is
how a rule ends up enforced in three places and bypassed in a fourth.

| Layer | Owns | Does NOT own |
|---|---|---|
| **Models** | persisted relations, database constraints, state vocabulary, cheap object-local methods | multi-model workflows, provider calls, pricing |
| **Services** | multi-model transactions, pricing and entitlement decisions, provider orchestration, anything used by more than one entry point | request parsing, HTTP status codes |
| **Serializers** | wire validation and representation of the DTO | authorization, domain transactions |
| **Views / viewsets** | request parsing, authentication, permission selection, status codes, mapping a domain error to a response | business rules |
| **Tasks** | thin, idempotent execution entry points | reusable business logic |
| **Admin** | an operator interface over existing domain actions | being the only place an action is implemented |

Two rules follow from the table:

- **MUST**: a database-enforceable invariant lives in the database. A
  constraint the model can express and a service checks instead is a
  constraint two concurrent requests can violate.
- **MUST NOT**: let a serializer become a hidden service layer or an
  authorization bypass. Validation that decides *whether the actor may* is a
  permission, not a field rule.

**A task is not a place to put logic.** Put the behaviour in a service so it
can be tested without a worker, and let the task be the entry point that calls
it. A task carrying its own business rules is untestable in the fast suite and
unreachable from any other caller.

## Dependencies and boundaries

Depend **inward** through named service methods or model/query contracts.

**AVOID**: view-to-view calls, circular imports between apps, and importing a
sibling's private helper. Reaching past an app's public surface makes its
refactor your outage.

- A cross-domain **read** that is stable and cheap may be an explicit query.
- A cross-domain **state transition** needs an owner and a transaction
  boundary — not two apps each writing half of it.

**A shared module is earned, not assumed.** Do not move product-specific logic
into a common module merely because two call sites look similar. Two things
that look alike and change for different reasons are not one thing; merging
them creates a module with two masters and no owner.

## A nested app keeps its boundaries

Where a product surface is built as apps inside an app, those inner apps have
their own `AppConfig`, label, and migration history. **MUST**: retain those
boundaries. Flattening models or imports into the umbrella app merges two
migration histories that were deliberately separate, and that is not reversible
by editing code.

Registration, labels, admin loading and routing for that shape have their own
page: [Nested apps and super-apps](./nested-apps-and-super-apps.md).

## Adding an endpoint

Add one only when it makes **authorization, consistency, latency, or a client
contract** better.

**AVOID** adding an endpoint to relocate formatting, to expose a value a client
already has, or to duplicate an existing aggregate under a friendlier name. A
second route answering an existing question is a second answer that will drift.

## The registry is the truth about what is active

Wherever the project declares its active apps, queues, schedules and API
groups, **that declaration is the source of truth** — not the presence of a
directory on disk.

**MUST**: confirm a domain is registered before editing it. An archived or
unregistered app tree can look completely alive: it imports, it has tests, its
models are defined. Editing it produces work that ships nowhere, and the only
signal is that nothing changes.

## Review checklist

- Is this domain active and registered, rather than merely present on disk?
- Does every durable fact and mutation have exactly one owner?
- Is a database-enforceable invariant enforced by the database?
- Is the transaction boundary explicit where multiple records or provider calls
  participate?
- Could another entry point reuse the service without HTTP assumptions?
- Does a nested app retain its label and migration ownership?
