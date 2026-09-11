---
title: General Django Standard — index
status: current
version: "1.0"
audience: backend, platform, qa, agents
last_reviewed: 2026-09-01
---

# `general/` — how to write Python and Django

Rules that hold in **any** Django service, not only this one. A page here must
survive being read in a codebase that shares none of this one's apps,
dependencies, or domain.

**Nothing in this directory is copied anywhere.** There is no sibling Python
repository keeping a `@rules` tree, so there is no sync and no drift gate — see
[`../CLAUDE.md`](../CLAUDE.md).

## Read by task

| Work | Page |
|---|---|
| Writing or reviewing Python; comments; lint policy | [Python code quality](./python-code-quality.md) |
| Where a capability lives, who owns a fact, layer boundaries | [Architecture and ownership](./architecture-and-ownership.md) |
| Grouping several apps under one umbrella; nested app registration, labels, routing | [Nested apps and super-apps](./nested-apps-and-super-apps.md) |
| Changing models, constraints, schema, transactions | [Models, migrations, and transactions](./models-migrations-and-transactions.md) |
| Designing a service or a provider boundary; error policy | [Services, errors, and integrations](./services-errors-and-integrations.md) |
| Changing an endpoint, a serializer, or a generated contract | [API contracts and code generation](./api-contracts-and-codegen.md) |
| Enqueueing work, scheduling, webhooks, external side effects | [Background jobs and side effects](./jobs-and-side-effects.md) |
| Authorization, tenancy, secrets, money | [Security and tenancy](./security-and-tenancy.md) |
| Logging, diagnosing a live failure, running an incident | [Observability and incidents](./observability-and-incidents.md) |
| Writing tests, verifying a change, handing off | [Testing and verification](./testing-and-verification.md) |
| Writing docs, refreshing them after a wave | [Documentation governance](./documentation-governance.md) |
| Preparing work for coding agents, or working as one | [Agent-ready development](./agent-ready-development.md) |

Read the **whole page**, not a match inside it. A search returns the lines that
agree with the phrasing you already had in mind and hides the clause that would
have changed what you did.

## Normative language

- **MUST**: required for correctness, safety, or a gated invariant.
- **SHOULD**: the default; deviate only with a written reason.
- **MAY**: optional and context-dependent.
- **AVOID**: usually harmful; prove the exception.

## What belongs here, and what does not

A page qualifies only if it stays true in a service with different apps, a
different domain, and a different deployment.

**Belongs:** which layer owns a decision, how a migration stays deploy-safe,
what makes a job retry-safe, how tenant scope is derived, what a comment must
carry, how to read a red test, how to run an incident.

**Does not belong**, and is the recurring failure mode:

- An app, model, module, or path name.
- A command, a Makefile target, a settings module.
- An environment variable, a queue name, a permission class.
- A framework this project happens to use — django-cfg has
  [its own directory](../djangocfg/README.md).
- A worked example built on this product's domain.

Where a rule is universal but its *enforcement* is local, state the rule here
and let [`../custom/`](../custom/README.md) name the command. "A job MUST be
idempotent" is portable; naming the queue is not.

**The test before adding a line:** would this sentence be *false* — not merely
irrelevant — in an unrelated Django project? If yes, it belongs elsewhere.

Keeping evidence is encouraged; keeping its **address** is not. "A selection of
four rule families produced 1,171 findings, so it was narrowed to five rules"
teaches the lesson anywhere. The same sentence with a file path attached only
teaches it here.
