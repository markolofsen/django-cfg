---
title: Testing This Service
status: current
version: "1.0"
audience: backend, qa, agents
last_reviewed: 2026-09-10
---

# Testing This Service

There is no CI ([`gates-and-verification.md`](./gates-and-verification.md)), so
a test is evidence only when a person ran it and read the number. This page is
what that run needs to know here specifically.

## What actually runs the suite

The suite is written for **pytest** — `pytestmark`, parametrize, fixtures — and
`pytest.ini` configures it.

```bash
.venv/bin/python -m pytest apps/catalog/ apps/normalizer/tests/ -q
```

`make test` runs the same thing: `check_editable --strict`, then
`.venv/bin/python -m pytest` with no path arguments. It and a direct invocation
collect the same 2310 tests (measured 2026-09-10).

> **Changed 2026-09-10.** `make test` previously ran `manage.py test`, Django's
> own runner, which reads neither `pytest.ini` nor pytest-only constructs and
> so collected almost nothing. The headline command in the Makefile ran
> something other than what everyone calls "the suite". Earlier revisions of
> this page told you to treat it as the editable-install gate it wraps — that
> advice is withdrawn; it is now the suite.

`pytest.ini` sets `DJANGO_SETTINGS_MODULE = api.settings.base`. **There is no
separate test settings module** — `api/settings/` holds `base.py` and
`config.py` and nothing named `test`.

**Verify against `pytest.ini` before quoting it.** As of 2026-09-10 it sets
neither `testpaths` nor `asyncio_mode`, and this handbook has claimed both. It
*does* now set `--reuse-db`, which it did not when that correction was written.

## Scope the run

`norecursedirs` excludes `e2e/` and `modules/.arhcive/` (sic — the typo is the
directory's real name) because those fail at *import*, and a collection error
aborts the whole run before one test executes. Markers cannot help: `-m` filters
after collection.

Name the app directories you touched. A bare `pytest` from the root collects
more than you mean and takes the failure of an unrelated tree as yours.

## The database trap

`pytest.ini` sets **`--reuse-db`**, so `test_mls` and `test_mls_estate` are kept
between runs and nothing is dropped. **After a migration changes the schema the
reused databases are stale** and must be rebuilt.

Run once with `--create-db` to rebuild them.

> **Fixed 2026-09-10, needs django-cfg ≥ 2.3.1.** `--create-db` used to fail
> against itself: the django-cfg pytest plugin dropped the test database while
> the same process still held a connection on the *other* alias, and Postgres
> refuses to drop a database with open sessions. It read like the dev-server
> conflict above but was not — the server holds `mls`/`mls_estate`, not the
> test databases. On an older django-cfg it still fails; drop them with `psql`
> until the venv has the fix.

**Two checkouts share one set of test databases.** They are named from the
settings, not from the directory, so a second agent or worktree testing at the
same time TRUNCATEs your data mid-run. A measurement taken while another run is
in flight is not evidence. Check before trusting a number:

```bash
ps aux | grep -c "[p]ytest"
```

> **Changed 2026-09-10.** `--reuse-db` was not set until then, and every run
> dropped and recreated both databases. Postgres refuses to drop a database
> with open connections, so the run ERRORed with `database "test_mls" is being
> accessed by other users … There are 11 other sessions using the database`.
> The holder was ordinarily nothing broken — measured that day, one idle
> `manage.py runserver 8013`, 14 hours old, holding 20 connections across both
> databases.

That failure is gone with the flag set, but the shape is worth keeping: a run
that ERRORs rather than FAILs, naming a database instead of an assertion, is
telling you **your code never executed**. If you hit it after a `--create-db`,
find the holder before killing anything:

```bash
psql -d postgres -tAc "select datname, state, count(*)
  from pg_stat_activity where datname is not null and datname<>'postgres'
  group by datname, state;"
```

Then either run the one app directory alone, or stop the server holding the
pool — **ask first if it is not yours.** In a shared tree it belongs to
someone, and a long-running server is often mid-task.

## A truncating test rolls back further than its own rows

`django_db(transaction=True)` rolls back by TRUNCATE-ing every table rather
than aborting a transaction. That removes rows seeded by **data migrations**,
which no later test restores — here `catalog.0029_portal` and its neighbours.
Everything downstream then fails with `Portal.DoesNotExist` or
`PropertyLifestyle.DoesNotExist`: measured 2026-09-10, 8 to 133 failures
depending on collection order.

This is why the trade in the section above is not free. Recreating both
databases every run silently repaired the damage, so a real defect stayed
invisible for as long as the harness was paying to rebuild the world. **A
harness that hides a bug is not cheaper than one that shows it.**

**MUST**: before adding `transaction=True`, establish that the test needs a
real transaction — one that asserts a signal is merely *connected* usually does
not, and the flag is then pure cost and blast radius.

**MUST NOT** read a `Portal.DoesNotExist` in an unrelated test as that test's
bug. Run the file alone first. If it passes in isolation and fails in the
suite, you are looking at ordering, not logic.

## Not every test needs a database

Twenty-three test files here declare no `django_db` at all, and that is the
preferred shape when it fits. A pydantic validator, a pure function, a prompt
fragment — the class is the whole surface:

```python
def test_a_small_recurring_price_labelled_sale_becomes_rent():
    assert BaseListingResponse(
        deal_type="sale", rental_period="monthly", price=2800
    ).deal_type == "rent"
```

No fixtures, no database, ~0.07s for fifteen cases. A validator test that
saves an `Asset` to assert a field is testing Django, not the rule.

## Pin what the rule must NOT do

The rules in this service exist because a naive version of them was wrong, and
the naive version is what a later reader will reach for. Negative cases are
where that knowledge survives.

Two worked examples, both from `apps/normalizer/tests/`:

- `test_tenancy_cadence_gate.py` — "a `rental_period` means it is a rental" is
  false: 96 published sales carry one, and the expensive ones are genuine
  income properties. The test that a $3.9M monthly listing stays a **sale** is
  what stops someone simplifying the rule back.
- `test_sqft_area_gate.py` — 290 published rows have a building legitimately
  larger than their plot. The tests at 1x, 2x, 3x and 9x are the reason the
  band is bounded on both sides rather than being `building > land`.

Write the measurement into the docstring. "290 rows sit between 1.1x and 9.5x"
tells the next reader why the constant is what it is; "checks the ratio" does
not.

## Related

- [`two-databases.md`](./two-databases.md) — why `databases=["default",
  "estate"]` is mandatory, and what `DatabaseOperationForbidden` means.
- [`gates-and-verification.md`](./gates-and-verification.md) — every other
  gate, and who runs it.
