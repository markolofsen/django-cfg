---
title: MLS Django Reference Profile
status: current
version: "2.0"
audience: backend, frontend, platform, agents
last_reviewed: 2026-09-06
---

# MLS Django Reference Profile

Where this service declares what it is: apps, API groups, queues, admin,
Constance, checks. Start here when you need to find a declaration rather than a
behaviour.

> **Retraction — `api/config.py` no longer exists.** Every v1 page that told
> you to edit it (13 pages named it) was pointing at a file that was split
> into `api/settings/config.py` plus `api/settings/builders/*.py`. Follow the
> map below, not a v1 path.
>
> **Second retraction, 2026-09-06.** This page was adapted from a sibling
> django-cfg service and kept two of *its* files in the map: `checks.py` and
> `constance.py` under `configs/`, plus an `api/settings/test.py`. None exist
> here, and the entries are removed rather than corrected — there is nothing
> to point them at. See the map for where each concern actually lives.

## The settings map

`api/settings/config.py` (383 lines) holds the `DjangoCfgConfig(DjangoConfig)`
class — the object django-cfg reads. It *composes*; it does not carry the long
declaration lists. Those live one directory down, one file per concern:

| Module | Owns | Go here when |
|---|---|---|
| `api/settings/builders/applications.py` | `build_project_apps()` — the installed-app list, in load order, annotated | adding, renaming or archiving an app |
| `api/settings/builders/openapi.py` | `enum_name_overrides` (25 pinned enums) + the OpenAPI groups (30 here; the CRM extension contributes 14 more) | adding an endpoint group or fixing a churning generated enum |
| `api/settings/builders/background.py` | RQ queues, health thresholds, the periodic schedule | adding a queue or a scheduled job |
| `api/settings/builders/admin.py` | Unfold navigation and admin composition | adding an admin section |
| `api/settings/builders/notifications.py` | notification wiring | changing how the service tells someone something happened |

Two concerns are **not** in that directory, and looking for them there is the
common mistake:

- **Constance** is declared inline in `config.py` (two fields today,
  `SITE_NAME` and `SITE_DESCRIPTION`). `manage.py check` prints the count.
- **System checks** live in the app that owns the invariant —
  `apps/catalog/checks.py` — not in a project-wide module. A check belongs
  beside the thing it guards, and `@register()` runs at import time, so the
  app's `ready()` is what connects it.

Two supporting modules sit beside `config.py`: `api/settings/base.py` and
`api/settings/builders/mcp.py`. There is **no separate test settings module**:
`pytest.ini` sets `DJANGO_SETTINGS_MODULE = api.settings.base`, so tests run
what everything else runs.

**MUST**: treat `build_project_apps()` as the truth about which domains are
active. A directory under `apps/` is not evidence — see
[`app-roster-and-domains.md`](./app-roster-and-domains.md) for the archived
trees that still import cleanly.

**MUST**: register a sub-app of a super-app by its full dotted path with an
explicit `AppConfig` class. An `apps/` sub-package shadows `apps.py` and Django
picks the wrong module otherwise. `applications.py` says this in a comment
because it was learned the hard way; do not "simplify" those entries.

**MUST NOT** re-add declaration lists to `config.py`. The split exists so a
person changing a queue does not scroll past eighty lines of enum pins, and so
a diff names its own concern.

## Stack

| Concern | Current implementation |
|---|---|
| Python | `requires-python = ">=3.12,<3.14"` (`pyproject.toml`); ruff and black both target `py312` |
| Django | `django>=5.2.0,<6.0` |
| Framework | `django-cfg[full]`, **unpinned by design** — see the contract gate in [`gates-and-verification.md`](./gates-and-verification.md) |
| Serving | uvicorn (ASGI), `api.asgi:application` |
| Background | django-rq, five queues on Redis DB 12 — [`background-work.md`](./background-work.md) |
| Realtime | django-cfg Centrifugo |
| LLM | `modules/django_llm` + `modules/llm_router.py`; ingestion in `apps/normalizer` |
| Extensions | `extensions/` holds django-cfg extension points; `apps/` and `modules/` under it are **empty** today |

This project declares roughly a dozen direct dependencies; there is no direct
HTTP client, Redis client, task queue or test framework in the list — all of
those arrive through `django-cfg[full]`.

> **Retraction, 2026-09-06.** Two sections here described a `carapis-crm` uv
> workspace member at `extensions/apps/crm/` and a `CRM_CONFIG_DATA_DIR`
> `setdefault` that had to precede every CRM import. Neither exists in this
> service — `extensions/apps/` and `extensions/modules/` hold nothing but
> `__init__.py`. They were carried over from the sibling product this page was
> adapted from, and one of them was a `MUST NOT` about an import ordering that
> cannot occur. Both are removed rather than rewritten.

## Where commands run

All management commands run through the project venv. After
`make install-local` swaps django-cfg for the editable checkout, **use
`.venv/bin/python` directly** — `uv sync` and `uv run` revert django-cfg to the
published wheel, which is how a command that worked ten minutes ago starts
reporting an unknown flag.

```bash
make dev        # Django dev server, port 8000 (runserver)
make asgi       # uvicorn, port 8000
make rq         # RQ workers; queue list derived from settings.RQ_QUEUES
make run-all    # ASGI + RQ together
make kill-all   # stop everything
make check      # Django system checks
make config     # show resolved configuration
make migrate    # migrate_all
```

`make dev`, `make asgi` and `make run-all` kill the port first (`kill-ports` /
`kill-all` are prerequisites), so a stale process does not silently keep the
port and leave you testing the old code.

## Production

**Django source is bind-mounted into the containers**, so an app-code change
needs a **restart, not a rebuild**: `make -C projects/docker restart-django`.
`projects/docker/CLAUDE.md` states it, and both things are true at once: the
image carries a copy, and the running containers mount the checkout over it.
The frontend is the opposite case and the mistake to avoid — it is **not**
mounted, so a frontend change needs `make redeploy-frontend`.

**Environment changes still need a restart.** The process reads them once at
startup, so a `git pull` that updates a dotenv leaves the old values in memory.

**A dependency change needs a rebuild**, not a restart.

## Review checklist

- Did you edit a declaration in `api/settings/builders/`, rather than pushing it
  back into `config.py`?
- Is the app you edited present in `build_project_apps()`?
- If you added a sub-app, does it carry a full dotted `AppConfig` path?
- Does the change need a container restart, a rebuild, or both?
- If you ran a management command, was it `.venv/bin/python` rather than
  `uv run`?
