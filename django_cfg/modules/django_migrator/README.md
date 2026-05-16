# django_migrator

State-validated multi-database migration orchestrator for django-cfg.

Replaces the legacy `MigrationManager` with a layered, typed module that
introspects the physical database before issuing any DDL — so deploys
fail loudly on drift rather than half-succeeding and surfacing as a
`ProgrammingError` deep inside a request handler hours later.

## Why this exists

Django's built-in `migrate` command works fine for single-database
projects. As soon as you split apps across multiple connections, you
hit operational issues the docs don't cover:

1. **`migrate <app> --database=X` bypasses the router** — Django assumes
   you know what you're doing and applies DDL unconditionally. Per-app
   loops in helper scripts therefore route incorrectly the moment
   routing rules change. Plain `migrate --database=X` (no app filter)
   respects the router, but then needs every app's `allow_migrate` to
   be correct.

2. **`django_migrations` drifts from actual DDL.** Manual hotfixes,
   partial restores, interrupted runs, parallel agents — all create
   silent drift that surfaces hours later as `column does not exist` or
   `relation already exists`.

3. **`TEST.MIRROR` leaks into production.** The setting lives in
   `DATABASES` permanently, not just during tests. A naive router
   collapses the routed alias onto its source in production, silently
   routing writes to the wrong DB.

4. **No drift detection.** Django trusts `django_migrations` and never
   compares it against the live schema.

This module addresses all of the above with one consistent lifecycle.

## Architecture

```
django_migrator/
├── types.py                   — DriftIncident, DriftReport, DbReport,
│                                MigrationReport, MigratorOptions,
│                                GuardResult, RewindPlan, LoadedMigration
├── exceptions.py              — MigratorError + specific subclasses
├── logger.py                  — MigratorLogger (stdout + Python logger)
│
├── introspection/             — Read-only schema + history inspection
│   ├── apps.py                — AppInspector: apps ↔ DB routing
│   ├── schema.py              — PostgresSchemaInspector: information_schema
│   ├── history.py             — MigrationHistoryReader: MigrationLoader wrapper
│   └── drift.py               — DriftDetector: compare history vs schema
│
├── repair/                    — Reconcile history with reality
│   ├── primitives.py          — fake_apply / fake_rewind helpers
│   ├── fake_detector.py       — Companion-field detector registry
│   └── engine.py              — RepairEngine: orchestrate repairs
│
├── orchestration/             — High-level coordination
│   ├── guards.py              — Pre-flight guards (connection, mirror, locks)
│   ├── extensions.py          — PostgreSQL extension installer adapter
│   └── manager.py             — Migrator: main entry point
│
├── reporting/                 — Output formatting
│   └── formatter.py           — TextReportFormatter
│
└── tests/                     — Unit tests (38 cases)
```

Each layer depends only on the layers below it. `tests/` covers pure
logic (types, logger, formatter, fake detector); integration tests with
real Postgres live at the project root.

## Drift classification

A drift incident has one of three directions:

| Direction | Meaning | Symptom on next migrate | Repair |
|---|---|---|---|
| `recorded_missing` | `django_migrations` has the row, DDL never ran. | `ProgrammingError: column does not exist` when ORM uses the field. | Fake-rewind to before the drifted migration → plain `migrate` re-applies forward. |
| `unrecorded_present` | DDL effects exist, no record in `django_migrations`. | `ProgrammingError: relation already exists` when `migrate` tries to recreate. | Fake-apply the missing record (zero DDL effect). |
| `half_applied` | Unrecorded migration where `CreateModel` ran but follow-up `AddField` did not. | Same as `unrecorded_present`, but rewinding would recreate the existing table. | Fake-apply + warning ("table exists, some columns missing — add a follow-up migration manually"). |

Foreign tables (tables on this DB whose app is routed elsewhere) are
listed but never auto-touched — dropping anything is always explicit.

## Public API

```python
from django_cfg.modules.django_migrator import (
    Migrator,
    MigratorOptions,
    MigratorLogger,
    TextReportFormatter,
    register_fake_detector,  # for django_currency-style companion fields
)

migrator = Migrator(
    options=MigratorOptions(
        repair=True,            # auto-fix drift before migrating
        dry_run=False,          # True = forensic check only, no DDL
        interactive=False,      # CI mode
        skip_makemigrations=False,
        verbosity=1,
    ),
    log=MigratorLogger(),       # or pass stdout/style/logger explicitly
)

report = migrator.migrate_all()
print(TextReportFormatter().render(report))

if not report.all_clean:
    raise SystemExit(1)
```

For ad-hoc forensic checks:

```python
report = migrator.check()      # never mutates anything
for db in report.db_reports:
    print(f"{db.alias}: drift={db.drift.total_drift_count() if db.drift else 0}")
```

## Management commands

### `python manage.py migrate_all`

Run the full lifecycle across every database in `DATABASES`.

```bash
# Default: detect drift, abort if found, otherwise migrate
python manage.py migrate_all

# Forensic check only — no DDL, no record changes
python manage.py migrate_all --check

# Auto-repair drift, then migrate
python manage.py migrate_all --repair

# CI mode — no interactive prompts
python manage.py migrate_all --repair --non-interactive

# Skip the makemigrations step (faster when migrations are already up to date)
python manage.py migrate_all --skip-makemigrations
```

Exit code is `0` when the report is clean for every database, `1`
otherwise. Drift detected without `--repair` is non-zero so CI fails
fast.

### `python manage.py migrator`

Interactive menu for day-to-day developer flow. Also exposes single-DB
and single-app migrations.

```bash
# Open the menu
python manage.py migrator

# Skip the menu, run full migration without prompts
python manage.py migrator --auto
python manage.py migrator --auto --repair

# Migrate one database alias only
python manage.py migrator --database vehicles

# Migrate one app across every DB that owns it
python manage.py migrator --app catalog
```

The interactive menu offers: full migrate, full migrate with `--repair`,
forensic check, `makemigrations` only, per-DB migrate, and status view.

## Per-database lifecycle

```
For each alias in DATABASES (default first, then alphabetical):

  1. Guards
     ├─ connection_live           — SELECT 1, fail early on dead DB
     ├─ test_mirror_isolation     — refuse if MIRROR is actively routing
     │                              writes in non-test mode
     └─ no_concurrent_migration   — detect another migrate holding the
                                    Postgres advisory lock

  2. DriftDetector.scan(alias)
     → returns DriftReport with three classified lists

  3. If drift detected:
     ├─ --repair: RepairEngine.apply()
     │    ├─ fake-apply unrecorded_present (history catches up)
     │    ├─ fake-apply half_applied  + warning for manual recovery
     │    └─ fake-rewind recorded_missing (so plain migrate re-applies)
     └─ otherwise: stop, add error to DbReport, exit 1

  4. Companion fake-apply (django_currency etc.)

  5. call_command("migrate", database=alias)
     — no app filter, router's allow_migrate is the decision point

  6. Verify: no migrations pending for apps owned by this alias
```

## Guards

| Guard | Fatal? | What it catches |
|---|---|---|
| `connection_live` | yes | Bad creds, dead host, typo'd alias. |
| `test_mirror_isolation` | yes | `TEST.MIRROR` actively redirecting writes outside of test mode. Detects by comparing physical DB NAMEs; passes silently if NAMEs differ (mirror configured but inactive). |
| `no_concurrent_migration` | yes | Postgres advisory locks held by another process. Prevents hanging on a long-running parallel migrate. |

All three live in `orchestration/guards.py`; new guards are added by
appending to `DEFAULT_GUARDS` or passing a custom tuple to
`GuardSet(...)`.

## Companion-field detector

Some fields auto-create a hidden DB column via `contribute_to_class`
(e.g. `django_currency.MoneyField` adds a `_currency` column when the
parent `Decimal` column is declared). The migration recorded for that
hidden column would fail with "already exists" because the column was
created implicitly. Field implementations register a predicate at
import time:

```python
from django_cfg.modules.django_migrator import register_fake_detector
from django.db import migrations as dj_migrations

def is_currency_companion(op):
    if not isinstance(op, dj_migrations.AddField):
        return False
    return getattr(op.field, "is_companion_currency_field", False)

register_fake_detector(is_currency_companion)
```

The orchestrator runs through unapplied migrations once at the start of
each per-DB run and fake-applies any whose ops all match a detector AND
whose columns physically exist.

## Configuration

Routing rules come from `settings.DATABASE_ROUTING_RULES`, which
django-cfg generates from each `DatabaseConfig.apps` field:

```python
# api/config.py
databases: Dict[str, DatabaseConfig] = {
    "default": DatabaseConfig.from_url(url=env.database.url),
    "vehicles": DatabaseConfig.from_url(
        url=env.database.url_vehicles,
        apps=["catalog", "catalog_api", "normalizer", "intelligence"],
        test_mirror="default",  # only honored when NAMEs match (test mode)
    ),
}
```

Models in `apps=[...]` route to `vehicles`; everything else stays in
`default`. The orchestrator never overrides this mapping — it only
respects what the router does.

## Testing

Unit tests live in `tests/` and require no Django setup beyond
`DJANGO_SETTINGS_MODULE`:

```bash
DJANGO_SETTINGS_MODULE=api.settings pytest -p no:django \
    src/django_cfg/modules/django_migrator/tests/ -v
```

38 cases cover: types & report logic, logger formatting and nesting,
fake-detector registry, text report formatting (including drift
classification rendering, half-applied section, repair summary,
truncation of long lists).

Integration tests against real Postgres are out of scope for unit suite
— see `@dev/@refactoring10-multidb/07-testing-strategy.md` for the
layout (two service containers, drift simulation fixtures, full
lifecycle assertions).

## Caveats

- **No FDW orchestration.** Cross-DB joins are still developer-handled
  (UUIDField + manual lookup pattern, see `VehicleChatCardView` in the
  CarAPIs project for an example).
- **No `db_constraint=False` enforcement.** Refactor plan Phase 05
  introduces a Django system check for this; not implemented yet.
- **`RemoveField` / `RenameField` not detected as drift.** These are
  reversible and Django's autodetector tracks them through model state.
  Symptom of drift here is "column has wrong name" which surfaces at
  query time, not migrate time.
- **Half-applied migrations require manual recovery.** The auto-repair
  fake-applies them to unblock further migrations, but recreating the
  missing columns is a manual step (add a follow-up migration or
  restore from backup).

## Design rationale

See `src/django_cfg/@dev/@refactoring10-multidb/` for the full design
documents and the research (`research/results.md`) that informed the
architecture.
