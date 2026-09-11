---
title: django-cfg Capability Map
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# django-cfg Capability Map

Before adding infrastructure code, check whether django-cfg already owns the
capability. **MUST**: reuse public APIs; **MUST NOT** copy internals into this
repository. Inspect the current source under `~/djangocfg/src/django_cfg/` —
module docs and published versions can lag local behaviour.

> **Retraction.** Version 1.0 of this page listed the framework's capabilities
> as a flat table with no usage column, which read as though every row was in
> use here. It was not: roughly half of the listed modules exist upstream and
> are **not imported anywhere in this repository**, and two capabilities that
> *are* live here — payments and the mailer — had no row at all. The third
> column below fixes both halves. Presence in this table is evidence the
> framework **offers** something, never that this service uses it.

## The table

"In use here" is measured by imports and configuration in this repository, not
by the module existing upstream.

| Need | django-cfg capability | In use here |
|---|---|---|
| Users, OTP, JWT, OAuth | `apps.system.accounts` | **Yes** — the account surface of this service |
| TOTP second factor | `apps.system.totp` | **Yes**, narrowly |
| Transactional email content and locales | `apps.system.mailer` | **Yes** — backs the `load_email_content` command |
| Payments, checkout, subscriptions | `apps.payments` | **Yes**, but see the note below |
| Admin UX | `django_admin` | **Yes** — heavily (~90 files) |
| Admin theme | `django_unfold` | Indirect — a dependency of `django_admin`, not imported directly |
| Admin dashboard widgets | `django_dashboard` | **Available, not used here** |
| OpenAPI / client / ORM / WS generation | `django_generator` | **Yes** — owns the generated clients |
| FastAPI generation | `django_generator.fastapi` | Indirect only — reached through `ORMGenerator.FASTAPI`; no direct use |
| Background work | `django_rq` | **Yes** — heavily (~108 files) |
| LLM / vision / embeddings | `django_llm` | **Yes** — the largest surface (~282 files) |
| MCP server and tools | `django_mcp` | **Yes** (~48 files) |
| Realtime RPC and events | `django_centrifugo` | **Yes** (~17 files) |
| Email delivery | `django_email` | **Yes** (~7 files) |
| Operator alerts | `django_telegram` | **Yes**, narrowly — CRM notifications and LLM integration |
| Errors, slow queries, RQ failures | `django_monitor` | **Yes** (~7 files) |
| Structured logging | `django_logging` | **Available, not used here** |
| Public sitemap | `django_sitemap` | **Yes** (~4 files) |
| File lifecycle | `django_cleanup` + `StorageConfig` | **Available, not used here** |
| Health endpoints | `django_health` | **Available, not used here** |
| Money / currency display and conversion | `django_currency` | **Config enabled, no module import** — `CurrencyConfig` is set in `api/settings/config.py`; nothing imports the module |
| Multi-database migration and drift | `django_migrator` | **Available, not used here** — `migrate_all` is the operational entry point |
| Import / export | `django_import_export` | **Available, not used here** — present only as a transitive dependency |
| Open Graph images | `django_ogimage` | **Available, not used here** |
| DRF browsing theme | `django_drf_theme` | **Available, not used here** |
| Local exposure | `django_ngrok` | **Config enabled, no module import** — `NgrokConfig(enabled=True)` is set; development only, never production trust |

**On payments**: the framework ships `django_cfg.apps.payments`, and this
repository runs its own live `modules/payments/` domain — Stripe-first, with
the RQ schedules `reconcile_pending_payments` and `sync_stripe_subscriptions`
(both hourly, `low` queue, declared in `api/settings/configs/background.py`), a
`payments` OpenAPI group, and MCP tools. **Billing authority is a product
policy and stays here.** Do not migrate the domain upstream, and do not assume
the upstream app is what serves this service's money paths.

**Two "config enabled, no module import" rows are not a defect to repair.** A
configuration object being constructed is not the same as a runtime surface
being exercised. Treat those rows as "the switch is on, nothing reads it here"
and confirm before citing either as live behaviour.

## Adoption decision

Six steps, in order, before enabling a module that is available and not
currently used.

1. **Confirm the module is active and configured.** The registry is
   `api/settings/config.py` (the `DjangoCfgConfig(DjangoConfig)` class) plus
   `api/settings/configs/` — apps in `configs/applications.py`
   (`build_project_apps()`), OpenAPI groups and `enum_name_overrides` in
   `configs/openapi.py`, RQ queues and schedules in `configs/background.py`.
   Confirm the installed package version too.

   > **Retraction.** Version 1.0 of this page pointed step 1 at `api/config.py`.
   > **That file no longer exists** — it was split into `api/settings/config.py`
   > and the six modules under `api/settings/configs/`. A reader following the
   > old instruction found nothing and could reasonably have concluded the
   > registry was gone.

2. **Read its public exports, current tests and non-archived docs.** Exports
   win over prose; see the inspection order in
   [`working-with-the-framework.md`](./working-with-the-framework.md).
3. **Decide whether the behaviour is reusable framework policy or this
   product's domain policy.** This is the upstream-vs-here question and it is
   answered before code is written, not after.
4. **Prefer composition through a small adapter** over deep or internal
   imports. An adapter is one file to change when the framework moves; a
   scattered internal import is a search.
5. **Verify the security, tenant, failure and operational contracts.** A
   framework default is a default, not a decision about this service's tenancy.
6. **If changing the framework**, use `make install-local`, update the upstream
   tests and public docs, then verify here against **both** the local editable
   and the published package.

## Enabling a module is not free

**MUST NOT** enable a module merely because it exists. Every enabled runtime
module adds some of: startup hooks, middleware, signals, URL routes, scheduled
jobs, dependencies, or data exposure. Each of those is a surface that must be
operated, and several are invisible until something fails.

**MUST**: record the owner when a module is enabled, and disable an unused
surface rather than leaving it configured. A configured module nobody owns is
the row that becomes wrong on this page next.

## Review checklist

- Did you check this table — and the module's current source — before writing
  new infrastructure code?
- Is the capability genuinely absent here, or listed as "available, not used"
  because nobody has adopted it yet?
- For a newly enabled module: what startup hooks, middleware, signals, routes,
  schedules and data exposure does it add, and who owns them?
- Does the adoption reach the framework only through public exports, via an
  adapter rather than scattered internal imports?
- If a row's usage status changed as a result of this work, was this page
  updated in the same session?
