---
title: CmdOp Django Engineering Standard
status: current
version: "2.0"
audience: backend, frontend, platform, qa, agents
last_reviewed: 2026-09-01
---

# CmdOp Django Engineering Standard

How to evolve the CmdOp Django service. It is a decision standard, not a
substitute for executable configuration, tests, or the nearest app README.

```text
general/    how to write Python and Django — true in any Django project
djangocfg/  the django-cfg framework: what it owns, how to use it, how to
            change it. It lives in ANOTHER repository.
custom/     this service: its apps, domain, config, gates, contracts
v1/         the previous single-level handbook, superseded
```

**Start here:** [`general/README.md`](general/README.md) ·
[`djangocfg/README.md`](djangocfg/README.md) ·
[`custom/README.md`](custom/README.md) — each maps a task to its page.
How to read and change this directory: [`CLAUDE.md`](CLAUDE.md).

## Why three directories

The split separates **a judgment you must apply** from **a fact you must look
up** — and, uniquely here, from **a contract owned by another repository**.

django-cfg is neither universal (in an unrelated Django project it is absent,
so its module names would be false) nor part of this service (its source,
tests and release cycle live in `@projects/djangocfg/`). Giving it its own
directory makes the routing question explicit rather than accidental.

Mixing these is how a handbook rots as one piece: a reader who finds a dead
path stops trusting the paragraph above it, which was fine.

## What this standard optimizes for

In priority order:

1. Correct tenancy, authorization, billing, and external side effects.
2. Stable API and generated-client contracts.
3. Explicit domain ownership and local changes.
4. Recoverable background work and observable production behavior.
5. Fast, evidence-based delivery **without CI**, and without disturbing other
   agents working in the same tree.

## Normative language

- **MUST**: required for correctness, safety, or a gated invariant.
- **SHOULD**: the default; deviate only with a written reason.
- **MAY**: optional and context-dependent.
- **AVOID**: usually harmful; prove the exception.

## The short version

- **`api/settings/`** owns the active registry, OpenAPI groups, RQ queues and
  schedules. `apps/@archive/` is deliberately not loaded — do not infer active
  behavior from a directory's presence on disk.
- Models own persisted invariants, services own multi-step domain actions,
  serializers own wire validation, viewsets own HTTP policy. A task is thin.
- Evolve schema through additive, deploy-safe migrations; old and new code MUST
  be able to run simultaneously at every stage.
- Tenant scope, actor identity, price and entitlement are **server-derived**.
  Never accept them from a client as authorization truth.
- Make jobs idempotent and retry-safe; enqueue only after the state they consume
  is committed.
- **Never hand-edit a generated client or an applied migration.**
- **There is no CI and there never will be.** Every check runs when a person
  runs it — except the one gate wired into the Docker build.
- A behavior change updates the affected README or handbook page in the same
  change.
- Another agent may be working in this tree right now: never stash, reset or
  revert files outside your task.

## Sources of truth

1. Executable configuration, models, migrations, tests, and public package
   exports.
2. The affected app's README and nearest local instruction file.
3. This handbook for cross-app policy and the quality bar.
4. Approved `@dev/` plans only when the task explicitly implements that plan.

When prose and executable behavior disagree, preserve the executable behavior
until the owner decides otherwise, then correct the documentation in the same
change.

## Maintaining the standard

- Generalize a rule to `general/` only with evidence beyond one app, and strip
  the identity from it: keep a failure's shape, drop its address.
- Service-specific facts go in `custom/` or the nearest app README; framework
  facts go in `djangocfg/`.
- **A number is a claim.** If you quote a count, quote the command that produced
  it, and re-run it when you touch the page.
- Where you correct a claim that was genuinely false, leave a short visible
  retraction. A reader who learned the wrong fact needs to see it named.
