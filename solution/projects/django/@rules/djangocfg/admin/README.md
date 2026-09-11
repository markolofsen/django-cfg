---
title: Django Admin
status: current
version: "2.0"
audience: backend, support, operations, agents
last_reviewed: 2026-09-01
---

# Django Admin

Django Admin is an **operator surface** for inspecting records and carefully
performing domain actions that already exist. It is **not** a shortcut around
authorization, lifecycle rules, services, or auditability.

That framing decides most design questions on the sibling pages. An admin
screen is a view onto a domain, so the domain must be able to do the thing
without the admin — see
[`../../general/architecture-and-ownership.md`](../../general/architecture-and-ownership.md),
where Admin owns "an operator interface over existing domain actions" and
explicitly does not own "being the only place an action is implemented".

## `PydanticAdmin` and `AdminConfig`

The admin base classes come from django-cfg
(`django_cfg.modules.django_admin`). Standalone model screens here inherit
`PydanticAdmin` so the operator experience, widgets and framework behaviour
stay consistent. `AdminConfig` is the preferred declaration for new screens and
for meaningful redesigns.

**The two names are imported from different places, and this is deliberate:**

```python
from django.contrib import admin

from django_cfg.modules.django_admin import AdminConfig, BadgeField
from django_cfg.modules.django_admin.base import PydanticAdmin
```

- **`AdminConfig` is exported from the package** — along with `ActionConfig`,
  `BadgeField`, `CounterBadgeField`, `FieldsetConfig`, `ResourceConfig`,
  `DocumentationConfig` and `Icons`. Import these from
  `django_cfg.modules.django_admin`.
- **`PydanticAdmin` is deliberately NOT in the package `__all__`.** It is
  commented out there with the reason: importing it at package level would
  touch the model layer during import and raise `AppRegistryNotReady`. Import
  it from `django_cfg.modules.django_admin.base`.

**MUST**: use `.base` for `PydanticAdmin`. **MUST NOT** "fix" this by adding it
to the package export or by importing it from the package — the omission is the
guard, and the failure it prevents appears at Django startup, far from the
import that caused it. This is the one case in this repository where importing
a name absent from `__all__` is correct; it is not licence to do so generally
(see the inspection order in
[`../working-with-the-framework.md`](../working-with-the-framework.md)).

Existing complex screens **MAY** retain native `ModelAdmin` attributes and
methods on top of `PydanticAdmin` until a focused redesign; that keeps service
actions and permissions stable. Django inline classes remain native inlines.

## Read next

- [Patterns and safety](./patterns-and-safety.md) — design, read-only records,
  actions, query performance, verification.
- [Composition and decomposition](./composition.md) — file boundaries, operator
  workflows, progressive disclosure, migration policy.
- [django-cfg reference map](./reference.md) — the upstream docs and source
  route map, and the framework change loop.
- [Working with the framework](../working-with-the-framework.md) — aliases,
  local source, editable install.

The primary upstream reference is
`~/djangocfg-docs/features/modules/django-admin/`; app-level guidance is
`~/djangocfg-docs/guides/app-design/admin.mdx`. The implementation is
`~/djangocfg/src/django_cfg/modules/django_admin/`.

## Review checklist

- Is every action on this screen also reachable without the admin, through a
  service?
- Is `PydanticAdmin` imported from `.base` and `AdminConfig` from the package?
- Does the screen expose only what an operator needs — no secrets, key
  material, raw payment payloads, or cross-tenant data?
- Was every framework symbol used here confirmed against the current exports in
  `~/djangocfg`, not copied from an older example?
