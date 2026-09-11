---
title: Background Jobs and Side Effects
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# Background Jobs and Side Effects

A queue makes work asynchronous; **it does not make it exactly once.** A job can
be delayed, retried, duplicated, or executed after a newer state exists. Every
rule here follows from that one sentence. The project's queues, workers and
schedules are in [`../custom/`](../custom/README.md).

## The job contract

- **Queue a small identifier and immutable input** — not a live model instance,
  a request object, a credential, or a large mutable payload. A serialized model
  is a snapshot that was already stale when it was written.
- **Commit the intent before enqueueing.** Use a post-commit hook when a
  transaction creates the record the job consumes.
- **The task reloads its state and re-validates the transition** before acting.
  The world moved between enqueue and execution; a job that trusts its arguments
  is asserting that it did not.
- **The task calls an idempotent service method.** Keep the task thin so the
  behaviour is testable without a worker.
- **Repeated execution MUST NOT duplicate** a charge, an email, a provisioning
  action, a counter, or a notification. Use unique records, state checks,
  idempotency keys, and the provider's own idempotency support.
- **Separate a retryable failure from a terminal one.** A network timeout should
  retry; a validation or authorization failure should not, and retrying it just
  burns the queue. Log enough structured context to diagnose the outcome without
  logging secrets or user payloads.

## Scheduled work

A scheduled function MUST be idempotent and safe when a run overlaps its
predecessor or the worker was down and several fire at once.

**AVOID** letting a management command quietly become a second scheduler. An
operator-run command is a deliberate act; the same logic on a cron is a system,
and a system with two schedulers double-runs.

## External providers and webhooks

Treat a provider call as an **unreliable boundary**.

- **Authenticate the callback and verify its signature before parsing any
  business meaning from it.** A webhook body is attacker-controlled until
  proven otherwise.
- **Record the provider event or idempotency key**, so a redelivery is
  recognised rather than reprocessed.
- **Reconciliation is the authority when the provider owns the final state.**
  Billing is the clearest case: a successful checkout *response* does not make a
  subscription active — the reconciled webhook does. Code that grants access on
  the response grants it on an outcome the provider may still reverse.

**MUST NOT** perform slow, non-idempotent network work while holding a database
transaction. Persist the intended transition, call the provider outside the
transaction, then record the authoritative result or failure.

## Review checklist

- Can this task run **twice**, and run **late**, safely?
- Is it enqueued only after the state it consumes is committed?
- Are queue choice, timeout, retry behavior and failure observation explicit?
- Does a webhook authenticate and reconcile rather than trust the payload?
- Does any provider call happen while a transaction is open?
