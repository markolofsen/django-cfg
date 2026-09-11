---
title: django-cfg Admin Reference Map
status: current
version: "2.0"
audience: backend, operations, agents
last_reviewed: 2026-09-01
---

# django-cfg Admin Reference Map

The django-cfg admin module is an **owned dependency** and may be inspected or
fixed at source. This page routes a task to the canonical material; it
deliberately does not duplicate every `AdminConfig` or field option, because
those move on the framework's release cycle and a copy here would go stale
silently.

## Where to look

All paths below resolve through the `~/djangocfg-docs` alias established by
`scripts/setup_alias.sh` — see
[`../working-with-the-framework.md`](../working-with-the-framework.md).

| Need | Canonical documentation |
|---|---|
| Overview and quick start | `~/djangocfg-docs/features/modules/django-admin/index.mdx`, `quick-start.mdx` |
| `AdminConfig` options | `~/djangocfg-docs/features/modules/django-admin/configuration.mdx` |
| Display and formatting fields | `~/djangocfg-docs/features/modules/django-admin/field-types/` |
| Filters | `~/djangocfg-docs/features/modules/django-admin/filters.mdx` |
| Flash messages | `~/djangocfg-docs/features/modules/django-admin/flash-messages.mdx` |
| In-admin documentation surface (`DocumentationConfig`) | `~/djangocfg-docs/features/modules/django-admin/documentation.mdx` |
| Worked end-to-end examples | `~/djangocfg-docs/features/modules/django-admin/examples.mdx` |
| Complete public surface | `~/djangocfg-docs/features/modules/django-admin/api-reference.mdx` |
| App-level composition | `~/djangocfg-docs/guides/app-design/admin.mdx` |

> Version 1.0 of this page listed seven rows and omitted `documentation.mdx`
> and `examples.mdx`, which both exist in that directory. The omission was not
> harmful in itself, but it made the table read as a complete inventory when it
> was a selection — treat the directory listing, not this table, as the
> authority on what documentation exists.

`field-types/` contains `index.mdx`, `basic-fields.mdx`, `display-fields.mdx`,
`formatting-fields.mdx` and `advanced-fields.mdx`.

## The implementation

```text
~/djangocfg/src/django_cfg/modules/django_admin/
├── __init__.py    # the package __all__ — the public surface
├── base/          # PydanticAdmin lives here (base/pydantic_admin/)
├── config/        # AdminConfig, ActionConfig, FieldsetConfig, and the rest
├── icons/  models/  utils/  widgets/  templates/  static/
```

**MUST**: confirm the current import surface there when a documentation example
fails. **MUST NOT** guess an export, or copy an internal module path into this
repository.

Note that `base/` is a package, not a `base.py` module — but the import is
unchanged: `from django_cfg.modules.django_admin.base import PydanticAdmin`.
The reason `PydanticAdmin` is not exported from the package `__all__` is in
[`README.md`](./README.md).

## Decision order

1. Start from the **operator's job** and permission level.
2. Decide whether the record is editable, action-only, or read-only — the
   classification table in [`composition.md`](./composition.md).
3. Select list fields, filters, search, ordering and relation loading.
4. Choose **built-in django-cfg display fields before writing custom HTML**.
5. Route mutations through the domain service and preserve audit behaviour.
6. Verify changelist, detail, permissions, actions and query behaviour — see
   [`patterns-and-safety.md`](./patterns-and-safety.md).

## Updating the framework

When work here reveals a **reusable** admin defect:

1. Change it in `~/djangocfg`.
2. Run the django-cfg test suite **from that repository**.
3. Update the public documentation content when the user-facing contract
   changes.
4. Reinstall or sync the local package and verify the affected admin here.

**MUST**: a local editable fix is **not shipped** until the django-cfg package
is versioned and published and this repository returns to the published
dependency. Until then the fix exists on one machine, and code here that
imports a new symbol from it will crash-loop on the server — `pyproject.toml`
requests `django-cfg[full]` unpinned, so nothing catches the gap locally.

**MUST NOT**: patch `site-packages` or a copied package as a shortcut around
that loop.

## Review checklist

- Was the framework API confirmed against the current exports in `~/djangocfg`,
  or only against a documentation example?
- Does the change belong upstream (reusable admin behaviour) or here (this
  product's operator workflow)?
- If it went upstream: were the upstream tests run and the public docs updated
  in the same change?
- Does any new import here exist in a **published** release, not only in the
  local editable tree?
- Did any path this page names get verified to resolve before it was written?
