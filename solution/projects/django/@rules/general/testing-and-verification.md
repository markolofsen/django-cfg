---
title: Testing and Verification
status: current
version: "2.0"
audience: backend, qa, agents
last_reviewed: 2026-09-01
---

# Testing and Verification

A backend change is complete when **its important contract runs**, not when its
edited file imports. Test the risk the change introduced. The commands and
gates for this service are in
[`../custom/gates-and-verification.md`](../custom/gates-and-verification.md).

## The verification ladder

Climb only as far as the change requires, but start at the bottom:

1. Focused tests for the service, model transition, parser, or view contract.
2. Framework checks and the affected app's tests.
3. Migration and generated-contract checks when a contract changed.
4. Worker, provider or integration behavior when asynchronous or external
   effects changed.
5. Runtime inspection after a deploy or an incident.

**Choose the narrowest relevant target first.** A full suite run that takes
minutes teaches you nothing a two-second focused run would not have, and the
delay is what makes people skip it.

**Know which runner a suite needs.** Where a project has both a framework
runner and a fixture-based runner, some suites only work under one of them.
Inspect the target module rather than assuming one runner covers both styles —
a suite that silently collects zero tests reports success.

**MUST NOT claim a coverage percentage, a lint gate, or a type checker that is
not configured and actually run in this repository.** "Tests pass" and "the
change is correct" are different claims, and the distance between them is the
set of contracts no test exercises.

## What to test, by risk

- **Domain services**: the valid transition, the invalid transition, an
  **idempotent retry**, and the permission or tenant boundary.
- **API**: authentication, authorization, serializer error shape, success shape,
  conflict, pagination and ordering, and **no cross-tenant leakage**.
- **Jobs**: task arguments, safe replay, queue invocation, failure handling.
  **Mock the queue or provider at the boundary**, not the service under test —
  mocking the service means the test proves the mock works.
- **Migrations**: forward behavior, defaults and backfill, and compatibility
  with the code deployed *during* the migration window. That last one is the
  case that breaks production and never breaks locally.
- **Webhooks and payments**: signature validation, **duplicate delivery**,
  intermediate provider state, and eventual reconciliation.

**Test the branch where the invariant is hard to hold**, not only where it
obviously holds. An idempotency guarantee exercised only on the first call is
untested.

## Reading a red test

When a test goes red after your change, **first ask whether the test is stale**
— asserting retired behavior — before "fixing" the code to satisfy it. Compare
the age of the test against the age of the feature. A test rewritten to match a
regression locks the regression in.

## Delivery discipline

- **Inspect version-control status before editing and before handoff.** Treat
  unexplained changes as another worker's in-progress edit.
- **MUST NOT** reformat, regenerate, revert, stash or reset files outside the
  task. A repository may be actively changed by another agent at the same time.
- **Distinguish a baseline failure from one your change introduced.** Report
  both; fix only yours.
- **Report what was verified, what was skipped, and what remains.** A report
  that lists only successes is not a report.

## Review checklist

- Does the change's **riskiest** contract have a test, or only its easiest one?
- Is an idempotent retry actually exercised?
- Do job tests mock at the boundary rather than mocking the thing under test?
- Can old and new code both pass during the migration window?
- Was a red test checked for staleness before the code was changed to match it?
- Does the report state what was skipped, not just what passed?
