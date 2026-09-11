---
title: Models, Migrations, and Transactions
status: current
version: "2.0"
audience: backend, data, agents
last_reviewed: 2026-09-01
---

# Models, Migrations, and Transactions

The database is the durable authority for persisted invariants. Model code,
constraints, migration history, and deployed data evolve as **one contract**.
The project's own migration commands and multi-database story are in
[`../custom/`](../custom/README.md).

## Model design

- Use model fields and `TextChoices` for persisted vocabulary. Reuse an enum
  across domains only when its meaning **and lifecycle** are genuinely shared —
  two domains that happen to have the same three states today will diverge.
- **MUST**: put uniqueness, check rules and referential integrity in database
  constraints when the database can enforce them. **Serializer-only validation
  is race-prone**: two concurrent requests both pass the check and both write.
- Use explicit `related_name` and explicit deletion behavior. **A cascade is a
  business decision**, not Django's convenient default — decide whether the
  child should die with the parent, and say so.
- **Store canonical facts.** Derive cheap deterministic presentation values
  rather than persisting a second copy that can drift from the first.
- Public identifiers should be stable and non-secret. A UUID or slug reduces
  enumeration risk but **does not replace authorization**.
- Index measured query paths and integrity lookups. Every index costs writes and
  storage; do not add one for an imagined future filter.

**QuerySets and managers own composable, database-shaped reads** — tenant
scope, published state, relation loading. Services own workflows, external
calls, and multi-model decisions.

**MUST NOT** hide a write or a provider call inside something that looks like a
harmless queryset filter. A reader who sees `.for_org(org)` expects a `WHERE`
clause, not a network round trip.

## Migration discipline

- **Generate migrations from the owning app and read the file before running
  it.** A generated migration is code, not an unquestioned artifact.
- **MUST NOT** edit or replace a migration that may have run in any shared
  environment. Move the schema forward with a new migration instead. A rewritten
  migration produces a database whose history no longer describes it, and
  nothing detects that until a fresh environment diverges from production.
- **Split risky changes into compatible stages:** add nullable or
  default-safe schema → deploy compatible code → backfill in bounded batches →
  enforce the constraint → remove the old field once consumers have migrated.
  Old and new code MUST be able to run simultaneously at every stage.
- **Use historical models inside `RunPython`.** Never import today's model class
  into a data migration: it carries today's fields and today's defaults, and it
  will fail — or worse, silently do the wrong thing — when replayed.
- Keep data migrations deterministic, resumable where practical, and mindful of
  locks and table size. **AVOID loading an entire table into memory.**
- A nested app owns its own label and migration package. Preserve explicit
  labels; do not relocate migrations into an umbrella app.

The routine safety checks:

```bash
manage.py makemigrations --check --dry-run   # does the code have unmigrated changes?
manage.py showmigrations                     # what is applied where?
manage.py sqlmigrate <app_label> <name>      # what SQL will this actually run?
```

`sqlmigrate` before a risky migration is the cheapest way to discover that an
"add a column" also rewrites the table.

## Transactions and concurrency

- **Put a transaction around a domain invariant that spans multiple writes** —
  not around an entire request, and never around a slow provider call. A
  transaction held open across a network call holds locks for the duration of
  someone else's outage.
- **A Python `if` before `save()` is not concurrency control.** Where concurrent
  workers or requests can transition the same record, use `select_for_update()`
  or an atomic conditional update, so the database decides the winner.
- **Register a post-commit side effect with `transaction.on_commit()`** when it
  consumes newly committed state. Enqueueing inside the transaction races the
  commit: the worker can start, read, and find nothing there.
- Make transaction retries safe, and keep external idempotency keys stable
  across those retries.

## Review checklist

- Is the invariant enforced at the strongest appropriate layer — the database
  where the database can do it?
- Is deletion behavior deliberate, and safe across tenants?
- Can old and new code coexist during every stage of the migration?
- Could two concurrent requests or jobs both pass the check and both write?
- Is post-commit work triggered only after durable state exists?
