---
title: App Roster and Domains
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-02
---

# App Roster and Domains

A **route map**, not a set of descriptions. `CLAUDE.md` at the repo root owns
what each domain means; this page tells you which apps exist, how big they are,
and where a new fact belongs.

Counts are `.py` lines excluding migrations, from
`find apps/<name> -name '*.py' -not -path '*/migrations/*' | xargs wc -l`.
Re-run it rather than trusting the number.

> **Rewritten 2026-09-02.** v1 of this page described a different service
> entirely — `apps/marketplace` (53k lines), `apps/build` (32k), `torrents`,
> `billing`, `organizations`, `apps/@archive/`. **None of those exist here.**
> Its `catalog` was "pricing inputs: plans, tiers, regions"; ours is the
> property catalogue. If you are reading a rule that names an app not in the
> table below, it is inherited from the sibling service — see the note in
> [`../../CLAUDE.md`](../../CLAUDE.md).

## Top level — `apps/`

Twelve entries under `apps/`. `core`, `_configs` and `_lib` are support
packages, not product domains; `_caribbean` and `_indonesia` are **empty brand
containers** — reserved addresses for apps only one portal would install, with
no `AppConfig` and nothing registered. See
[`../../@dev/completed/brand-app-containers/PLAN.md`](../../@dev/completed/brand-app-containers/PLAN.md)
and each container's own `README.md`.

> **Corrected 2026-09-06.** This table listed `indonesia` as a support package.
> It was neither a support package nor an app: `git ls-files apps/indonesia`
> was empty, and the directory held only stale `.pyc` files from a cadastre
> draft removed in `6ea28fb`. Renamed to `_indonesia` and emptied; recover the
> draft from that commit if the cadastre is ever built.

| App | `.py` lines | `@docs/` | Note |
|---|---:|:---:|---|
| `catalog` | 11,614 | — | **the core domain**: `Asset` (a real property), `Listing` (one source's advert for it), `Project` (a development). Owns the public read API, discovery vocabularies and dedup. |
| `normalizer` | 10,093 | yes | LLM ingestion — raw scraped text → a normalized `Asset`. |
| `ai_photo` | 2,313 | yes | operator-triggered photo editing jobs. |
| `inquiries` | 2,009 | — | inbound leads: concierge briefs, newsletter signups. |
| `api_keys` | 1,706 | — | service authentication via `X-API-Key`. |
| `storefront` | 1,667 | — | server-rendered public pages and sitemap sources. |
| `operations` | 929 | — | parser run tracking and listing sync. |
| `profiles` | 469 | — | user profiles on top of django-cfg accounts. |
| `intelligence` | 488 | — | valuation and undervaluation scoring. |
| `core` | — | — | support package |

Beyond `apps/`: `modules/` holds reusable capabilities (`django_llm`,
`llm_router.py`), `extensions/` holds django-cfg overlays (`apps/` and
`modules/` under it are empty today), and `mcp/` is the MCP tool surface.

**`api/settings/` is the authoritative registry** — `config.py` composes, and
`configs/` holds the lists: apps, OpenAPI groups, RQ queues and schedules.

> **Corrected 2026-09-06.** This line said the opposite — "`api/config.py` …
> Not `api/settings/`" — which was not merely a stale path but a statement
> pointing away from the right directory. `api/config.py` has not existed
> since the split. Map in
> [`settings-reference-profile.md`](./settings-reference-profile.md).

## Two databases

| Alias | Database | Holds |
|---|---|---|
| `default` | `mls` | accounts, sessions, admin, RQ |
| `estate` | `mls_estate` | the whole catalogue domain |

This is a routing boundary, not a performance detail. A test touching catalogue
models **MUST** declare both:

```python
@pytest.mark.django_db(databases=["default", "estate"])
```

Without it the failure is `DatabaseOperationForbidden`, which says nothing
about the assertion that actually matters.

## Where a new domain goes

Ask what owns the durable fact, not what the feature is called.

- A fact about **a property itself** → `catalog`. `Asset` is the real-world
  thing; `Listing` is one source's claim about it. Do not collapse them — the
  whole dedup design rests on the distinction.
- A fact **derived from raw source text** → `normalizer`. If an LLM produced
  it, it belongs to the ingestion domain, not the catalogue.
- A fact about **what a property is worth** → `intelligence`.
- A fact about **a parser run or a sync** → `operations`.
- A fact about **someone who contacted us** → `inquiries`.

**AVOID** a new top-level app for a surface that is only a read of an existing
domain. A second app answering an existing question is a second answer that
will drift.

## The public catalogue gate

`Asset.objects.public_catalog()` is the single definition of what a visitor may
see: published + public + active + a canonical slug + a non-member cluster role
**and at least one visible photo**.

The photo clause is the one that surprises people. An asset with every flag set
and no `Media` row seeds fine, returns 200 from nothing, and is invisible
everywhere — a page with no image reads as broken, so the catalogue withholds
it. **A fixture that expects an asset to be returned must give it a photo.**

## Review checklist

- Is the app you are editing in the table above, and registered in
  `build_project_apps()` (`api/settings/builders/applications.py`)?
- Does the fact you are persisting already have an owner in another app?
- If it touches catalogue models, does the test declare both databases?
- If it should be publicly visible, does it satisfy every clause of
  `public_catalog()` — including a photo?
- Did you read the app's own `@docs/` (where it has one) rather than this table?
