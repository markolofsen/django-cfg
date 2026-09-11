---
title: Django Admin Patterns and Safety
status: current
version: "2.0"
audience: backend, support, operations, agents
last_reviewed: 2026-09-01
---

# Django Admin Patterns and Safety

## Choose the smallest correct admin

For a simple model a colocated `admin.py` is sufficient. For a rich domain with
several models, use an `admin/` package with focused modules re-exported from
`admin/__init__.py` — see [composition](./composition.md). **MUST**: register a
model exactly once.

**SHOULD**: prefer django-cfg's declarative configuration when it gives a
clearer operator surface:

```python
from django.contrib import admin

from django_cfg.modules.django_admin import AdminConfig, BadgeField
from django_cfg.modules.django_admin.base import PydanticAdmin

config = AdminConfig(
    model=Subscription,
    list_display=["organization", "status_badge", "updated_at"],
    list_filter=["status"],
    search_fields=["organization__name", "stripe_subscription_id"],
    select_related=["organization"],
    readonly_fields=["id", "stripe_subscription_id", "created_at", "updated_at"],
    display_fields=[BadgeField(name="status_badge")],
)


@admin.register(Subscription)
class SubscriptionAdmin(PydanticAdmin):
    config = config
```

Note the two import lines: `AdminConfig` and the field types come from the
package, `PydanticAdmin` from `.base`. The reason is in
[`README.md`](./README.md) and it is not cosmetic.

The precise import surface and field options are framework APIs on the
framework's release cycle. **MUST**: verify them in the local django-cfg
exports or docs before copying an example — do not trust this snippet as an API
reference.

All standalone model admins here inherit `PydanticAdmin`. That does **not**
mean every legacy screen must immediately become one large `AdminConfig`:
native `list_display`, permission hooks, forms and service-backed actions are
valid on that base and form the safe migration bridge. **SHOULD**: convert to
declarative configuration when the screen is deliberately redesigned and the
result is clearer — not as a drive-by.

`admin.TabularInline` and `admin.StackedInline` are composition primitives, not
standalone screens, and **MAY** remain native Django classes. Keep them bounded
and read-only when they display history or evidence.

## Admin is not a lifecycle bypass

This is the section that earns the page.

- **MUST**: display authoritative external fields as read-only unless a
  controlled service owns their mutation — provider IDs, webhook records,
  hashes, generated keys, usage snapshots, timestamps.
- **SHOULD**: make audit, event and ingestion records append-only: disable add
  and change, and allow deletion only under an explicit operational policy.
- **MUST**: an admin action that changes business state invokes the **same
  service or domain transition** used by HTTP and jobs. **MUST NOT** use a bulk
  `queryset.update()` where it would skip validation, side effects, or
  reconciliation.
- **MUST**: a destructive action names its impact, uses Django's confirmation
  flow or equivalent deliberate friction, and records the actor where the
  domain requires it.
- **MUST NOT**: expose secrets, API-key material, raw payment payloads, or
  cross-tenant data without a documented support need. Treat admin users as
  privileged but not omniscient.

**Import/export is an explicit privileged workflow, not a free feature of an
admin base class.** Enable it only with a reviewed resource that allowlists
columns, validates tenant ownership and row bounds, rejects formulas and
dangerous files, previews errors, and routes mutations through safe domain
logic. Exports carry the same PII and secret minimisation and audit policy as
APIs; a large export belongs in a background job with expiring private output.

> `django_import_export` is currently present only as a transitive dependency —
> nothing in this repository imports it. Adopting it is an adoption decision,
> not a switch: see [`../capability-map.md`](../capability-map.md).

## Query and display quality

**Admin list pages are production queries.** They run against the same database
as everything else, and a list column that follows a relation runs once per row.

- **MUST**: configure `select_related` or `prefetch_related` for relations
  displayed in a list.
- **AVOID**: expensive computed fields in large lists.
- **SHOULD**: give operators searchable identifiers, and use semantic status
  badges rather than raw booleans where the state matters.

Make clear which fields are editable, computed, or provider-owned. Group
complex forms into fieldsets and collapse low-frequency diagnostics. An inline
is appropriate for a small bounded child set, never for an unbounded log or
history table.

## Verification

There is **no CI in this organisation**; every check below runs when a person
runs it and at no other time. Treat this list as the work, not as paperwork.

- Run `.venv/bin/python manage.py check`, then load the affected changelist
  **and** detail page with a permitted operator account. A screen that imports
  cleanly can still fail to render.
- Exercise every changed action **and its failure and permission paths**. The
  success path is the one least likely to be wrong.
- Check the query count or the generated SQL when a new list column follows a
  relation or computes per row.
- Confirm a read-only record cannot be altered through **any** path: add,
  change, delete, inline, or bulk action. Blocking four of the five is not
  read-only.
- Update the app's documentation when an admin action creates a durable
  operational workflow.

## Review checklist

- Does every state-changing action route through the same service that HTTP and
  jobs use?
- Are provider-owned and generated fields read-only, and evidence records
  immutable through every admin path?
- Does the changelist load its displayed relations, and has the query cost been
  measured on realistic row counts?
- Are secrets, key material and cross-tenant data absent from every column,
  fieldset and inline?
- Do destructive actions confirm, name their impact, and record the actor?
- Were the framework imports verified against current exports rather than
  copied from an older screen?
