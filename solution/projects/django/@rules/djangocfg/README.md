---
title: django-cfg — the framework directory
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# django-cfg

**django-cfg is an owned upstream framework that lives in another repository**
(`@projects/djangocfg/`, reachable here as `~/djangocfg`). It owns
configuration, app registration, OpenAPI and client generation, RQ, the admin
base classes, Centrifugo, LLM plumbing and the MCP surface. This service is
built on it, not merely dependent on it.

It gets its own rules directory because it is neither of the other two things:
it is not universal Django — in an unrelated project every `django_*` module
name here is simply false — and it is not this service's domain, because its
source, its tests and its release cycle are elsewhere and a fix there is not
shipped until the package is versioned and published.

## The standing rule

**MUST**: decide where a change belongs **before writing it**. Framework-level
behaviour with more than one plausible consumer goes upstream to
`~/djangocfg`; product policy, domain models, tenant rules and provider
integrations stay here.

Deciding afterwards produces the two expensive shapes: a domain rule buried in
a framework module where the next consumer inherits this product's policy, and
a framework fix written locally as a wrapper that must be maintained forever
because upstream never learned about it.

**MUST NOT** patch `site-packages`, a copied package, or a generated client.
See [`working-with-the-framework.md`](./working-with-the-framework.md).

## Read by task

| Task | Page |
|---|---|
| Set up local framework source; switch between editable and PyPI; understand a `check_editable` failure | [`working-with-the-framework.md`](./working-with-the-framework.md) |
| Decide whether a change belongs upstream or here | [`working-with-the-framework.md`](./working-with-the-framework.md) |
| Check whether the framework already owns a capability before building infrastructure | [`capability-map.md`](./capability-map.md) |
| Adopt a `django_*` module that is available but not yet used here | [`capability-map.md`](./capability-map.md) |
| Write or change an admin screen | [`admin/README.md`](./admin/README.md) |
| Admin safety, read-only records, actions, query cost | [`admin/patterns-and-safety.md`](./admin/patterns-and-safety.md) |
| Admin file layout, operator workflow, progressive disclosure | [`admin/composition.md`](./admin/composition.md) |
| Find the upstream doc or source for an admin API | [`admin/reference.md`](./admin/reference.md) |

Related, outside this directory:

- [`../general/architecture-and-ownership.md`](../general/architecture-and-ownership.md)
  — which layer owns a decision, in any Django project.
- [`../general/python-code-quality.md`](../general/python-code-quality.md) —
  one fact one owner, and when an abstraction is earned.
- [`../custom/README.md`](../custom/README.md) — this service's apps, domain,
  billing and tenancy.

## What this directory is not

It is not a copy of the upstream documentation. Where the framework's own docs
answer a question, these pages route to them
([`admin/reference.md`](./admin/reference.md) is the route map) rather than
restating an API that changes on the framework's release cycle, not this
repository's.

## Review checklist

- Did you decide upstream-vs-here **before** writing the change, not after?
- Does the change name a `django_*` module, a django-cfg export, or the loop
  for changing the framework — and is it therefore in this directory?
- If the change is upstream, is it accompanied by upstream tests and, when the
  public contract moved, upstream documentation?
- Did any path or symbol you wrote get verified against `~/djangocfg` rather
  than recalled?
