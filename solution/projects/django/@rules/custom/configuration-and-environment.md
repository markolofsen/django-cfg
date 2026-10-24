---
title: Configuration and Environment
status: current
version: "2.0"
audience: backend, platform, security, agents
last_reviewed: 2026-09-01
---

# Configuration and Environment

Two packages own runtime configuration here: `api/settings/` composes the
Django/django-cfg objects, and `api/environment/` parses deployment inputs into
typed values. Feature code consumes the resolved config; it does not parse
`.env` itself.

> **Retraction — `api/config.py` no longer exists.** v1's configuration page
> named it as the composition root. It was split on 2026-08-18; the map is in
> [`settings-reference-profile.md`](./settings-reference-profile.md).

## `api/settings/`

`api/settings/config.py` holds `DjangoCfgConfig(DjangoConfig)`. The declaration
lists live in `api/settings/builders/`: `applications.py`, `openapi.py`,
`background.py`, `admin.py`, `notifications.py`.

There is **no `constance.py` and no `checks.py`** here — those two belong to
the sibling service this page was adapted from. Constance is declared inline in
`config.py` (two fields), and system checks live in the app that owns the
invariant: `apps/catalog/checks.py`.

There is **no separate test settings module** either. `pytest.ini` sets
`DJANGO_SETTINGS_MODULE = api.settings.base`, so tests run the same settings as
everything else.

**MUST NOT** move a declaration list back into `config.py`.

## `api/environment/`

```text
api/environment/
  CLAUDE.md          the contract — read it before changing anything here
  .env.local         committed
  .env.prod          committed
  .env.local.example
  loader/            the parsing package
  tests/
```

`loader/` is seven domain modules plus a base: `_base.py`, `_catalog.py`,
`_config.py`, `_core.py`, `_crm.py`, `_notifications.py`, `_platform.py`,
`_realtime.py`.

> **Corrected 2026-09-06.** The list here named `_marketplace.py`,
> `_payments.py`, `_services.py` and `_storage.py` — the sibling service's
> modules. Ours are `_catalog.py` and `_crm.py`.

**SHOULD**: add a new variable to the domain module that owns it, not to
`_config.py`. The split exists so a catalogue variable is found by someone
reading catalogue configuration.

## Layering

`api/environment/loader/_base.py` documents the order, and it is the only
implementation of it:

1. environment variables with `__` notation (e.g. `EMAIL__HOST`)
2. `.env.local` if present — base runtime configuration
3. `.env.prod` on top, **when `IS_PROD` is set**
4. defaults from the pydantic field definitions

`ENV_DIR` is `Path(__file__).resolve().parent.parent` — `loader` is a package,
so it sits one directory *deeper* than the dotenv files, and that
`.parent.parent` is load-bearing. Getting it wrong **fails silently**: a
missing dotenv is skipped as normal (a dev checkout has no `.env.prod`), so a
wrong path yields an app running entirely on typed defaults with no error.

Nearly every test in `loader/tests/test_loader.py` patches `ENV_DIR` and so
cannot see that value being wrong. `EnvDirLocationTests` is the only guard on
the real path. **MUST NOT** delete or patch around it.

## The dotenv files are committed **on purpose**

`.env.local` and `.env.prod` are tracked in git (`git ls-files | grep '\.env'`
confirms both, plus `.env.local.example`). This is a deliberate decision, not a
leak:

- a checkout is runnable without a provisioning step;
- a rotation shows up in a diff.

The contract is `api/environment/CLAUDE.md`. The general handbook explicitly
defers to it — see
[`../general/security-and-tenancy.md`](../general/security-and-tenancy.md),
which states that whether dotenv files are committed is a project-level
decision and that the project's own contract must be checked before "fixing"
what looks like a leak.

**MUST NOT** "fix" this by removing the files, rewriting history, or proposing
a rotation. An agent applying the generic "never commit secrets" rule will
reach for exactly that; it is wrong here.

**MUST**: understand that **rotating a key means reissuing it at the
provider**, not editing the file. Editing the file alone leaves the old
credential live.

**MUST NOT**, separately, treat this as licence to widen the practice.
Credentials still do not belong in migrations, fixtures, generated clients,
logs, error responses or task arguments.

## `env_flag_enabled()` — the single boolean parser

`api/environment/loader/_base.py:60`. **This is the only place that answers "is
this flag on?"**

```python
env_flag_enabled("IS_PROD")
```

Truthy: `true`/`1`/`yes`/`y`/`t`/`on`, any case. Falsy: `false`/`0`/`no`/`n`/
`off`, **plus unset, empty, and unrecognised**.

Unset/empty/unrecognised are falsy **by choice**. Bare `TypeAdapter(bool)`
*raises* on `""`, and a process that exported `IS_PROD=` must resolve to "not
production" rather than crash the import of the settings module. An
unrecognised value is likewise falsy rather than fatal, because this runs
before logging exists — there is nowhere to report it.

**The failure it was written to end.** `IS_PROD` / `IS_TEST` / `IS_DEV` were
parsed in three independent places with two different rulesets.
`get_env_files()` and the CRM environment schema both hardcoded
`("true", "1", "yes")`; `EnvironmentMode` is a pydantic `BaseSettings` and used
pydantic's coercion, which *also* accepts `on`/`y`/`t`. The divergence was
one-directional and silent: **`IS_PROD=on` made `is_prod` True while
`get_env_files()` declined to load `.env.prod`** — production semantics running
on development secrets, with no exception raised anywhere.

`EnvironmentMode` cannot be the owner even though it is the widest parser:
`get_env_files()` is evaluated in the *class body* of `EnvironmentConfig`
(`env_file=get_env_files()` in `_config.py`), at module import — strictly
before any `EnvironmentMode` instance exists. The owner has to be callable at
that moment, so it is a module-level function. It delegates to the same
`TypeAdapter(bool)`, so the two cannot drift.

**MUST NOT** re-derive a flag with `os.getenv(...).lower() in (...)`. A
hardcoded tuple is narrower than pydantic's coercion, and a caller that narrows
it disagrees with `EnvironmentMode` about the same variable on the same boot.

## Behaviour-changing flags

Verified by reading their call sites. Where the fail direction is not obvious
from the code, it is marked so rather than asserted.

| Flag | Where | Default / fail direction |
|---|---|---|
| `IS_PROD` | `loader/_base.py:135` | unset → `.env.prod` not loaded; **fail-open to development config** |
| `IS_TEST`, `IS_DEV` | `api/environment/loader/_base.py` | via `env_flag_enabled`; unset is falsy |
| `CATALOG_EMBEDDING_ENABLED` | `apps/catalog/search/config.py` | **defaults to on** — the semantic lane's kill switch; read live, not at import, so it can stop a running process when a provider degrades |
| `CATALOG_EMBEDDING_THRESHOLD` | `apps/catalog/search/config.py` | a float, not a flag; the measurement that set it is in the comment beside it |
| `DJANGO_LLM_SOURCE` | `modules/django_llm` | which provider the LLM lane talks to |
| `DJANGO_CFG_GEN_NO_CACHE`, `DJANGO_CFG_GEN_PARALLELISM` | codegen | see [`api-groups-and-generation.md`](./api-groups-and-generation.md) |
| `REFERRALS_E2E_*` | `Makefile:138` | E2E parameters, not runtime config |

### One parser, and the one flag that used to disagree

**Fixed 2026-09-06.** `embedding_enabled()` in `apps/catalog/search/config.py`
parsed its own vocabulary — `not in {"0", "false", "no"}` — which is narrower
than `env_flag_enabled()`'s. The two disagreed on `off`, `n` and `f`: the
spelling that switches a flag off everywhere else in the process read as **on**
here.

The direction is what made it urgent. This is a kill switch, reached for while
a provider degrades, so an operator writing `=off` would have left the lane
running with no error and no log line.

> This page previously described the same defect in a sibling service's
> `MARKETPLACE_*` flags and a second parser called `environment_flag()`.
> Neither exists here. The defect class did, in our own file.

It is precisely what `env_flag_enabled()`'s docstring forbids: *"Do not
re-derive it with `os.getenv(...).lower() in (...)`: a hardcoded tuple is
narrower than pydantic's coercion, and a caller that narrows it disagrees with
`EnvironmentMode` about the same variable on the same boot."*

**MUST**: delegate parsing to `env_flag_enabled()`. A flag that needs a
different *default* — this lane is on unless someone turns it off, while the
helper treats unset as falsy — handles unset itself and delegates everything
else:

```python
raw = os.getenv(FLAG)
if raw is None or raw.strip() == "":
    return True          # this flag's default; the vocabulary is not ours
return env_flag_enabled(FLAG)
```

**MUST**: make an unrecognised value fail in the safe direction. For a kill
switch that means off — a typo must not leave it armed.

`apps/catalog/search/tests/test_kill_switch.py` holds the spellings, so the
narrowing cannot come back unnoticed.

**Unverified:** `CMDOP_USE_LOCAL_AGENT` appears only under
`apps/@archive/ai_chat/` — an unloaded app. Treat it as dead unless a live call
site is found.

**SHOULD**: route a new flag through `env_flag_enabled()` and record its fail
direction in the docstring at the call site. A flag whose fail direction is
undocumented is a flag nobody dares to flip in an incident.

## Constance is live

> **Retraction.** v1 wrote that "django-cfg *can* expose selected values
> through Constance", as a capability. It is configured and in use here — but
> inline in `api/settings/config.py`, not in a `builders/constance.py`. Two
> fields today: `SITE_NAME` and `SITE_DESCRIPTION`. `manage.py check` prints
> the count, which is the quickest way to confirm the wiring.

The scope rule still holds. Constance is for **low-risk operational and product
tuning that is safe to change without a deploy**.

**MUST NOT** put in Constance: secrets, database or cache endpoints, auth
policy, middleware, installed apps, queue topology, or anything that changes
the OpenAPI schema.

**MUST**: give every runtime-editable field a type, a range, a safe default, an
owner, and defined behaviour when the value is missing or temporarily
unavailable.

**AVOID** using Constance as a general feature-flag system. It has no rollout
or targeting semantics; a value changes for everyone at once.

## Validation

```bash
make check                                  # Django system checks
make config                                 # resolved configuration
.venv/bin/python manage.py check --deploy   # against prod-equivalent settings
```

`check --deploy` does not replace infrastructure, TLS, backup, host-validation,
cache/database or secret-store review. Django's system checks do **not** run in
the production request stack.

`show_config`, admin pages and startup summaries must redact recursively. A
pydantic `SecretStr` helps presentation but does not make an arbitrary model
dump safe.

## Review checklist

- Did you add the variable to the `loader/` module that owns its domain?
- Is a boolean read through `env_flag_enabled()`, or did you re-derive it?
- Is the fail direction of a new flag written down at its call site?
- Did you treat the committed dotenv files as a leak to fix? (They are not.)
- Does a rotation plan include reissuing at the provider, not just the diff?
- Does a new Constance field carry a type, range, default and owner — and is it
  genuinely deploy-free to change?
- Does the rollout note that an env change needs a container restart?
