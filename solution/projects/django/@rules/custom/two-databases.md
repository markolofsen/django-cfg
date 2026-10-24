---
title: Two Databases
status: current
version: "1.0"
audience: backend, platform, qa, agents
last_reviewed: 2026-09-10
---

# Two Databases

Requests touch **two** PostgreSQL connections. This is a routing boundary the
ORM enforces, not a performance detail you may ignore — and it is the first
thing that bites on a fresh checkout.

| Alias | Database | Holds |
|---|---|---|
| `default` | `mls` | accounts, sessions, admin, RQ |
| `estate` | `mls_estate` | the whole catalogue domain |

Declared in `api/settings/config.py` as a `databases` dict. `estate` names its
apps explicitly:

```python
"estate": DatabaseConfig.from_url(
    url=env.database.url_estate,
    apps=["catalog", "inquiries", "operations", "normalizer",
          "intelligence", "ai_photo", "calculators"],
)
```

**There is no hand-written router.** django-cfg derives routing from that
`apps` list, so an app is on `estate` because it is named there and nowhere
else. Adding a model to one of those apps needs no routing change; creating a
NEW app that FKs into the catalogue means adding it to the list, and forgetting
is not a warning — Django cannot follow a FK across databases, so the
relationship simply fails at runtime.

Geo reference data (`cfg_geo`) is on `estate` for exactly that reason: catalog
serializers resolve a source country to a `Country` row without crossing the
boundary.

## Neither database is created by `migrate`

If `mls_estate` is missing, every catalogue query fails with
`database "mls_estate" does not exist`, and nothing in the migration path
creates it.

```bash
createdb mls_estate     # once, on a fresh machine
make migrate            # = manage.py migrate_all
```

**MUST use `migrate_all`, never `manage.py migrate <app>`.** A bare `migrate`
targets `default`. Pointed at a catalogue app it reports success against the
wrong database and leaves `estate` untouched — a green line and no schema.

The deploy Makefile broke this rule until 2026-09-10 — its `migrate` target ran
`migrate`, `migrate --database=estate`, `migrate`, and only the middle line did
real work. It is `migrate_all` now.

**But that was untidiness, not the cause of what it looked like it caused.**
`default` carries 66 migration rows for apps whose tables live in `estate`, and
those rows are not removable: `migrate --database=default` runs every app in
`INSTALLED_APPS` against that database, and while the router blocks the table
creation, Django records `django_migrations` per *database*, not per table
owner. Deleting all 66 and running one `make migrate` restored all 66 in
seconds. Deleting only some is worse — dropping the catalogue apps while
leaving `calculators` orphaned `calculators.0001_initial → catalog.0024` and
every `migrate` on `default` then died with `InconsistentMigrationHistory`.

So the rows are ordinary output of a two-database setup. The schema is correct,
both databases report in sync. The only genuine removal is an `allow_migrate`
rule keeping Django off foreign apps in `default` — a router change, not a
cleanup.

## Tests must declare both

```python
pytestmark = pytest.mark.django_db(databases=["default", "estate"])
```

Without it the failure is `DatabaseOperationForbidden`, which names the
database and says nothing about the assertion that actually matters. A test
that touches any catalogue model needs this, including one that only reads.

A serializer test counts: instantiating `AssetPublicListSerializer` against a
saved row reads `estate`.

## What crosses the boundary and what does not

- **A ForeignKey may not.** Both ends must sit on the same alias. This is why
  `calculators` is on `estate` — its registries FK to `catalog.PublicMarket`.
- **A queryset may not join across it.** `Asset.objects.filter(user=…)` cannot
  reach an account row; carry the id and resolve separately.
- **A signal may.** Signals fire in process, so a handler on a `default` model
  can write to `estate` and vice versa. Nothing stops it and nothing warns.

## Related

- [`app-roster-and-domains.md`](./app-roster-and-domains.md) — which domain owns
  a fact, and therefore which database it lands on.
- [`testing.md`](./testing.md) — the `--reuse-db` trap and what actually runs
  the suite.
- [`settings-reference-profile.md`](./settings-reference-profile.md) — where
  the declaration lives.
