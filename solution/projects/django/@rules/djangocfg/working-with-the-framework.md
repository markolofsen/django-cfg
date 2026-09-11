---
title: Working with the django-cfg Framework
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# Working with the django-cfg Framework

This service is a django-cfg project, not a Django project with a third-party
dependency. Use the framework deliberately where it owns configuration, app
registration, OpenAPI generation, RQ, admin, Centrifugo, LLM or MCP; keep this
product's domain behaviour here unless it is genuinely reusable.

## Local source paths

The framework checkout is:

```text
/Users/markinmatrix/workspace/@projects/djangocfg/projects/django-cfg
```

Run its alias setup once on a new machine, or again when an alias is stale:

```bash
bash ~/djangocfg/scripts/setup_alias.sh
```

It establishes three stable symlinks:

```text
~/djangocfg       -> the django-cfg Python source (src/django_cfg/)
~/djangocfg-docs  -> the public documentation content
~/djangocfg-ui    -> the shared frontend packages
```

**MUST NOT** replace those symlinks with copied documentation, or hard-code a
developer-specific absolute path into reusable configuration. The aliases exist
so that a page like [`admin/reference.md`](./admin/reference.md) can name a
path that resolves on every machine.

## Local versus PyPI dependency

The default dependency resolves `django-cfg[full]` from PyPI. To develop
against the local source:

```bash
make install-local
.venv/bin/python manage.py check
```

`make install-local` syncs from PyPI first, then installs the local package in
editable mode and **removes the copied package from `site-packages`** so the
editable `.pth` path wins — `uv` copies files into `site-packages` even for an
editable install, and the copy would otherwise shadow the link.

**MUST**: after `install-local`, invoke `.venv/bin/python` directly. `uv sync`
and `uv run` restore the PyPI resolution and silently undo the editable link.
Run `make install` when returning to PyPI is what you actually want.

## `make test` checks the editable install first

`make test` runs two commands, in order:

```bash
.venv/bin/python manage.py check_editable --strict
.venv/bin/python manage.py test
```

The first is a prerequisite, not a test. `check_editable --strict` exits
non-zero when `django_cfg` resolves out of `site-packages` while a local
editable source is expected. **A reverted editable install therefore fails the
suite before a single test runs.**

What the failure means: something — usually a plain `uv sync` while adding an
unrelated dependency — reinstalled the PyPI copy over the editable link. The
error names it directly (`django-cfg loaded from PyPI copy (site-packages),
not your editable source`) and the fix is `make install-local`.

Why this is worth a startup cost: without the check, the same condition
surfaces later as an import-time pydantic error about some unrelated setting,
in every app at once — a symptom that points nowhere near the cause.

`--strict` is required. Without it the command reports the mismatch and still
exits 0, so the prerequisite would never bite. On a machine that never wanted
an editable install (no `~/djangocfg`, no `DJANGO_CFG_EDITABLE_EXPECTED`) the
check is inert and exits 0 — this is by design, not a gap.

## Inspection order before relying on an API

**MUST** inspect in this order; each step can correct the one before it.

1. **The public documentation** in `~/djangocfg-docs`. Relevant areas:
   `features/api-generation/`, `features/drf-guide/`,
   `features/modules/django-admin/`, `guides/app-design/`, `deployment/`.
2. **The installed package's public exports and the local source** under
   `~/djangocfg/src/django_cfg/`. Read the module's `__init__.py` `__all__`,
   not a docs example.
3. **This repository's own settings and tests** — principally
   `api/settings/config.py` and `api/settings/configs/`.

**Source and exports win when prose is stale.** A documentation example that
fails is a documentation defect: fix it in the owning framework workflow rather
than working around it here.

**AVOID** copying an internal module path out of a docs example. An export that
is not in `__all__` may still be a deliberate public import (see
[`admin/README.md`](./admin/README.md) for the `PydanticAdmin` case), but it
may equally be an internal that moves without notice — confirm which.

## Where a change belongs

**MUST**: decide before writing.

Change **upstream** (`~/djangocfg`) when the behaviour is framework-level, has
or should have more than one plausible consumer, and can be covered by tests
there.

Change **here** when it is product policy, a domain model, a tenant rule, a
provider integration, or a one-off composition. When in doubt, ask whether the
sentence would still be true for a different django-cfg consumer; if it names
this product, it belongs here.

**MUST NOT** patch `site-packages`, a copied package, or a generated client.
Those are outputs. An edit there survives until the next sync and then
disappears without a diff.

**MUST**: for a framework change that affects users, update the public
documentation in the owning docs workflow as part of the same change.

## A local editable fix is not shipped

**A local editable fix is not shipped until the upstream package is versioned
and published and this repository returns to the published dependency.** Until
then the change exists on one machine.

Two consequences that bite:

- **Release django-cfg before merging code here that imports a new symbol from
  it.** `pyproject.toml` requests `django-cfg[full]` unpinned, so a checkout
  can compile against a local working tree and still crash-loop on the server.
- After an upstream change, retest here against the local editable package
  **and**, before release, against the published version. Those are two
  different resolutions and only the second is what the server runs.

## Review checklist

- Was the upstream-vs-here decision made before the change was written?
- Does any new import here exist in a **published** django-cfg release, not
  only in the local editable tree?
- Was every framework path and symbol confirmed against `~/djangocfg` rather
  than recalled or copied from a docs example?
- Is the editable install still in effect (`manage.py check_editable`) after
  any dependency work in this repository?
- Did a framework change carry its upstream tests and, where the public
  contract moved, its upstream documentation?
