# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- **MCP OAuth: the consent page shows where the grant goes, and codes are single use.** The signed consent
  request (now uncompressed) carries `dest`, the validated redirect host (`claude.ai`, `127.0.0.1:3118`,
  `cursor://anysphere.cursor-mcp`), next to the client name; `<McpConsent>` shows both from that signed value
  ("Sends the result to ..."). Authorization codes are spent once through the Django cache (`cache.add`, no
  table); an unwritable cache refuses the exchange. Refresh tokens stay reusable; Renew key revokes them.

### Fixed
- **`POST /cfg/monitor/ingest/` answered 500 to a browser-like `Accept` header.** `MonitorIngestViewSet` had no
  `serializer_class`, and DRF's browsable-API renderer (picked for `Accept: text/html`) asks the view for one:
  `AssertionError: 'MonitorIngestViewSet' should either include a serializer_class`. The view now declares
  `serializer_class = IngestBatchSerializer` and answers JSON whatever `Accept` says. URL and payload are unchanged;
  a malformed body is a 400. Every other `GenericViewSet` in the package already declares its serializer.
- **Storage cleanup: a rollback no longer loses files, and shared files are kept.** `FileCleanupMixin.delete()`
  and `FileCleanupQuerySet.delete()` delete files in `transaction.on_commit` (they used to delete first, so a
  rolled-back delete lost the files while the row survived). The `post_delete` signal now honours
  `check_shared_files`, as its docs always said.
- **MCP: `McpKey` / `McpGrant` reverse names no longer clash with a project's own MCP models.** The user
  relations were `mcp_keys` / `mcp_grants` (Django check E304/E305 in projects that keep models of the same
  name); they are now `django_cfg_mcp_keys` / `django_cfg_mcp_grants` (in `0002` itself).
  The index names (`mcp_key_user_revoked_idx`, `mcp_grant_user_revoked_idx`, check E030) are prefixed
  `dcfg_` for the same reason: PostgreSQL index names are schema-wide, so a migration that creates
  `mcp_key_user_revoked_idx` fails when the project already has one.

### Added
- **MCP OAuth: `enable_public_profile(oauth=True)` needs no consent URL.** The approval page defaults to the Settings
  dialog of `DjangoConfig.site_url` (`<site_url>/#settings/mcp`); `oauth_consent_url` stays as an override and still
  enables OAuth on its own. `ProfileBuilder.enable_oauth()` takes `consent_url=None` too.
- **Storage delete sync (opt-in): row deleted, files in R2/S3 deleted, CDN purged.** `FileCleanupConfig(outbox=True)`
  writes `StorageDeletion` rows inside the transaction (new table, migration `0001` of `django_cleanup`); a worker
  (RQ schedule, `manage.py storage_outbox --drain`) deletes the files with retries and backoff, behind an
  `allowed_prefixes` allowlist, with `dry_run` and a `queue_only` mode for files another service owns.
  `register_owned_files(Model, keys=...)` declares prefixes or keys a model owns; `StorageConfig(cdn=CDNPurgeConfig(...))`
  purges the URLs from Cloudflare afterwards; `manage.py storage_orphans` reports files no owner claims (report only).
  Nothing changes until a project opts in. See `modules/django_cleanup/@docs/outbox.md`.
- **MCP tool hints.** `MCPTool` gains `read_only`, `destructive`, `idempotent`, `open_world`
  and `title`; `tools/list` now carries `title` and all four `annotations`. Claude and ChatGPT
  run a read-only tool without a per-call confirmation, so every built-in reader
  (`query_model`, `get_object`, `list_apps`, `aggregate_model`, ...) is marked, and a tool that
  declares nothing stays a prompting writer. `@mcp_tool` and `mcp.tool` accept `read_only=True`.

### Removed
- **MCP: the `McpKey` / `McpGrant` tables, the keys / connections / usage manage API (`django_mcp/manage`),
  the `AccessStore` protocol, `access_store=` / `stateful_oauth=`** (shipped in 2.3.352 to 2.3.354; one user,
  gptkino). The MCP credential is now the user's existing `UserAPIKey`. Migration `0003` drops
  `django_cfg_mcp_mcpkey` and `django_cfg_mcp_mcpgrant`; keys issued from them stop working, users copy
  their `UserAPIKey` instead. No new tables.

### Changed
- **MCP: the default key validator is the user's `UserAPIKey`.** `enable_public_profile()` with neither
  `key_validator` nor `public_keys` (and `ProfileBuilder.use_user_api_keys()`) accepts the key UUID, as
  `Authorization: Bearer` or `X-MCP-Access-Key`, through `auth.validate_user_api_key` (one indexed lookup,
  active users only). "Renew" is the existing `POST cfg/accounts/api-key/regenerate/`. An explicit
  `key_validator` is unchanged; the `operator` profile never accepts user keys.
- **MCP OAuth: tokens carry the key generation (`kg`).** Access and refresh tokens hold
  `UserAPIKey.reissued_at` in integer microseconds (0 when never regenerated or no key row); a token whose
  generation differs from the user's current one is refused (refresh answers `invalid_grant`), so
  regenerating the key ends every OAuth connection too. Tokens without `kg` count as generation 0, so
  tokens issued before this release keep working until the user regenerates. One extra query per check.
- **One browser-storage key scheme: `cfg.<area>.<name>`** (lower case, dots,
  `snake_case`). The generated client gains `helpers/keys.ts`: a registry of every
  key (`CFG_KEYS`, `CFG_FAMILIES`), guarded `read/write/remove` (SSR, private
  mode, quota), `clearAll()` for sign-out, `onChange()` for other tabs, and
  `createStorage('<owner>')` for apps (`storage.key('area', 'name')`).
  `helpers/auth.ts` uses it; the DPoP IndexedDB is now `cfg.auth.dpop`.
  Exported light from `@djangocfg/api/storage`. Rules: `@djangocfg/api/@docs/STORAGE_KEYS.md`.
  - **Breaking, no migration:** old keys (`cfg.access_token`, `auth_email`,
    `user_profile_cache`, `fm_session_id`, `djc.chat.*`, …) are not read. Signed-in
    users sign in once; the DPoP key is regenerated.
  - The Django-served admin bridge (`auth_token`, `refresh_token`), `NEXT_LOCALE`
    and `sidebar_state` keep their names.

### Added
- **MCP: OAuth 2.1 sign-in on a profile** (`django_mcp/oauth.py`). Claude (web,
  Desktop), ChatGPT, Claude Code, Codex, Cursor and VS Code connect by URL and
  sign in, with no pasted key. `mcp.enable_public_profile(..., oauth_consent_url=
  "https://my.example.com/mcp/connect", oauth_issuer="https://mcp.example.com")`
  or `ProfileBuilder.enable_oauth()`.
  - Stateless: client ids (RFC 7591), consent requests, codes and tokens are
    signed with `SECRET_KEY`; nothing is stored, no migration. PKCE S256 only.
  - Discovery at the host root: `/.well-known/oauth-protected-resource[/<path>/]`
    and `/.well-known/oauth-authorization-server`; endpoints under the profile
    (`<path>oauth/register|authorize|approve|token/`). A 401 on that profile
    answers `WWW-Authenticate: Bearer resource_metadata=...`.
  - The project's frontend identifies the user: `authorize` redirects to
    `consent_url?request=<signed>&client=<name>`, the page signs in with
    django-cfg auth and POSTs `{request, allow}` to `oauth/approve/` with the
    user's JWT, then navigates to the returned `redirect_to`.
  - Redirects only to the clients' own callbacks (claude.ai, chatgpt.com,
    platform.openai.com, `cursor://anysphere.cursor-mcp`, vscode.dev) or
    loopback. Checked against Claude Code 2.1 and Codex 0.146 on a local
    server; a test per client's callback shape.
  - The metadata does not advertise `authorization_response_iss_parameter_supported`
    (`iss` is still sent): Codex requires `iss` when it is advertised, then drops
    it from its loopback callback and fails the sign-in.
  - Guide: `@docs/connect-assistants.md` and the docs site page "Connect
    assistants" (backend line, consent-page contract, install-button links).
    A ready-made consent page and install widget for the frontend packages are
    not part of this release.
  - Every MCP endpoint now also reads the credential from `Authorization:
    Bearer`, so a per-user key works in bearer-only clients too.

### Changed (BREAKING)
- **MCP: authorisation is mandatory, there is no anonymous mode.** No MCP route
  answers without a credential: JSON-RPC, `GET <path>info/` and the agent chat
  all return `401` (`WWW-Authenticate: MCPAccessKey`) without a valid
  `X-MCP-Access-Key`. The only unauthenticated MCP routes are OAuth discovery
  and sign-in on a profile that enables OAuth (see Added).
  - Removed `access="anonymous"` (`MCPProfile`, `MCPConfigBuilder.profile`),
    `public_info` (config, profile, `set_public_info`) and
    `enable_public_profile(operator_public_info=...)`. Each raises `ValueError`
    with migration advice.
  - An enabled config with no key (no `access_key`, no `extra_keys`) now raises
    at build instead of serving open. `/info/` always needs the key.
  - `enable_public_profile()` needs a key path and the profile is key-protected:
    `key_validator="pkg.mod.func"` (`callable(key) -> user | True | None`, for
    per-user API keys in the project's DB) and/or `public_keys={"label": key}`.
    It serves only `public = True` tools; operator keys do not open it.
  - New `MCPProfile.key_validator` / `ProfileBuilder.set_key_validator`, and one
    credential check (`django_mcp/auth.py`) shared by JSON-RPC, `/info/` and
    agent chat. Static keys, `extra_keys` and `service_username` work as before.
  - Migration: keep `set_access_key()` for the operator, and give the public
    surface keys, e.g. `mcp.enable_public_profile(key_validator="api.mcp.validate_key")`.

### Added
- **`admin_access`: where the Django admin lives and who may reach it.**
  `AdminAccessConfig` on `DjangoConfig.admin_access`. Scanners probe `/admin/`
  on every host; the location and availability are now core-config settings,
  not a line hard-wired in each project's `urls.py`.
  - `enabled` (default `True`): `False` mounts nothing, so the route answers
    404, nothing links to it, and management commands are unaffected.
  - `path` (default `"admin/"`): the URL prefix. No leading slash, ends with a
    slash, URL-safe characters only, no `..`; anything else fails at startup.
  - `allowed_networks` (default `[]`): a CIDR allowlist (IPv4/IPv6). When set,
    any request under the admin prefix from outside it gets **404, never
    403**. The address is `REMOTE_ADDR`, which `RealIPMiddleware` rewrites from
    `CF-Connecting-IP` / `X-Forwarded-For`; that is only trustworthy when the
    app is reachable through the proxy alone. Defence in depth: the primary
    control belongs at the proxy (Traefik, Cloudflare).
  - Env, the same nested `__` style as `DATABASE__URL`: `ADMIN_ACCESS__ENABLED`,
    `ADMIN_ACCESS__PATH`, `ADMIN_ACCESS__ALLOWED_NETWORKS` (comma-separated or a
    JSON list). It works for a project that never mentions `admin_access`; a
    value passed in code wins over env.
  - One-line wiring: `*admin_urlpatterns()` (`from django_cfg import
    admin_urlpatterns`) replaces `path("admin/", admin.site.urls)` and returns
    `[]` when disabled. The old line keeps working untouched.
  - The framework's own staff surface under `/cfg/admin/` (dashboard tabs, the
    Next.js admin) follows the same `enabled` / allowlist rules.
  - New system checks, both warnings: `django_cfg.W011` (production with the
    admin at the default `/admin/`; suggests `secrets.token_urlsafe`) and
    `django_cfg.W012` (`admin_access` asks for a path or `enabled=False` but the
    admin is still mounted elsewhere, e.g. a hard-coded `path("admin/", ...)`,
    so setting only the env var would change nothing). **W011 becomes an error
    in a later release**; existing projects start unchanged today.
  - Anything that assumed `/admin/` now reads the configured prefix:
    `PublicEndpointsMiddleware`, admin login notifications, `NoIndexMiddleware`
    (no-store), dashboard quick actions, the `get_admin_url` tag, extension
    navigation links, the URL list and endpoint-status tools, the Unfold search
    and badge callbacks. With the admin disabled the dashboard quick actions
    omit it and `get_admin_url` returns `""`.
  - **Behaviour change:** `/cfg/admin/dashboard/` (staff-only, opened inside the
    admin) now answers 404 to anyone who is not staff, where it used to redirect
    to `admin:login`. The redirect failed with the admin disabled, and with a
    moved admin it told an anonymous scanner where the admin lives.
- **IndexNow — push changed sitemap URLs to Bing, Yandex, Seznam, Naver.**
  `IndexNowConfig` on `DjangoConfig.indexnow`. It reads the registered
  sitemap sources with the feed's template and fields, so IndexNow never
  announces a URL the sitemap would not list. How a run decides what to send
  is under **Changed** below.
  - RQ schedule, registered from the config (`schedule_interval`, `0` to turn
    it off). `manage.py indexnow_submit` runs it by hand.
  - `extra_urls`: a dotted path to `callable(since) -> list[str]` for pages
    the sitemap cannot see, such as deleted ones, 410s or redirects.
  - The key file is served at `/cfg/sitemap/indexnow/<key>.txt`; any other
    name returns 404. `indexNowKeyRewrite()` in `@djangocfg/nextjs/config`
    rewrites `/<key>.txt` to it, so the key lives in one place.
  - `indexnow.submit(urls)` never raises: it is meant for request paths, and
    an engine being down must not fail a save. `submit_changed()` raises
    `IndexNowError` on a refusal, so a failing job shows as failed.
  - Several sites on one backend: `sites=[IndexNowSite(host=…,
    source_suffix="-caribbean"), …]`. Each host takes its own sources and is
    submitted in its own request; one key serves every host.
  - Replaces two hand-rolled copies, one in carapis and one in cmdop, that
    had already diverged on error handling and on where the key lived.
- **Geo: selective country population.** `GeoConfig` gains a `countries`
  allow-list of ISO2 codes; `geo_populate` also accepts `--countries BB,BS,KY`
  (the flag overrides the config). States and cities cascade automatically to
  the selected countries.
  - Previously the only option was the full dr5hn dataset — ~250 countries,
    ~5,000 states, ~150,000 cities. A project serving a handful of markets had
    to import all of it, which bloats the database and lets reverse-geocoding
    resolve assets to places outside its coverage.
  - Measured on a five-market Caribbean project: **5 countries / 62 states /
    514 cities** instead of the full set.
  - Unknown ISO2 codes raise rather than silently importing nothing, and
    `GeoConfig` rejects country *names* (`"Barbados"`) at validation time — a
    typo that quietly dropped a market would otherwise surface much later as
    unresolved cities.
  - Default behaviour is unchanged: an empty list imports everything.

- **Payments engine — `django_cfg.apps.payments`** (production-lifted from a
  live SaaS): config-gated app driven by `PaymentsConfig` on `DjangoConfig`.
  - Provider abstraction (Stripe-first); the SDK is an optional extra:
    `pip install django-cfg[payments]` (also included in `[full]`).
  - One-time checkout with idempotency keys, zero-amount rejection, and
    TOCTOU race recovery.
  - Webhook ingestion: signature verification (secret rotation via
    comma-separated `STRIPE__WEBHOOK_SECRET`), `PaymentEvent` log with
    `event_id` idempotency, replay command.
  - Refunds, stuck-payment reconciliation (missed-webhook safety net), and a
    `payments_doctor` health report.
  - Host seams instead of hard couplings: swappable **owner model**
    (`CFG_PAYMENTS_OWNER_MODEL`, AUTH_USER_MODEL mechanism), **fulfillment
    hook** (dotted path + `payment_succeeded`/`payment_failed` signals),
    **owner resolver** for API views, **dunning mailer** hook.
  - Public in-memory `FakeProvider` at `django_cfg.apps.payments.testing` —
    a testable payments stack with no Stripe account.
  - Management commands: `payments_doctor`, `payments_listen`,
    `payments_reconcile`, `payments_refund`, `payments_replay_webhook`.
  - Subscriptions (Stripe Billing lifecycle) land in a later phase; the
    webhook path already accepts and safely skips those events.
- `payments` optional-dependency extra (`stripe>=15.3,<16`).

### Changed
- **Media stays on local disk outside production.** `StorageConfig.backend`
  now takes effect only when `env_mode` is production. Before this, a dev run
  or a test suite uploaded into the real bucket, and cleanup signals deleted
  objects there. In development and test every write and delete goes to
  `MEDIA_ROOT=<base_dir>/media`, with no opt-out. When the declared backend
  has a `custom_domain`, the default storage is
  `django_cfg.core.backends.storage.LocalStorageWithRemoteURLs`: `url()` of a
  file that is not on local disk returns the remote public URL
  (`custom_domain` + `environment`/`location`), so a database restored from a
  production dump still shows its media. Only `url()` falls back; `open()`,
  `exists()`, `size()` and `delete()` stay local. Without a `custom_domain` it
  is plain `FileSystemStorage`. `MEDIA_URL` is no longer derived from
  `custom_domain` outside production. Production settings are unchanged.
- **IndexNow remembers what it sent.** It used to submit whatever had a
  `lastmod` in a 25-hour window, which lost changes whenever a run failed and
  could not see removals. Each run now diffs every host's sitemap sources
  against `IndexNowUrl`, the last accepted state, and sends new, changed and
  removed URLs.
  - Only an accepted batch is recorded, so a failed run is retried.
  - The first run for a host records and sends nothing.
  - A source error, an empty read, or a shrink of more than `shrink_share`
    sends nothing.
  - At most `max_urls_per_run` per host per run; runs hold a cache lock.
  - Every POST is logged in `IndexNowSubmission`. Hosts and submissions show
    read-only in admin.
  - **Needs `manage.py migrate`** (`django_sitemap.0001`). The first run after
    upgrading seeds and sends nothing.
  - `IndexNowSite(key=…)` gives a host its own key. The key route answers
    every configured key.
  - `extra_urls(since)` now gets the host's last fully successful run.
  - `indexnow_submit` gains `--host` and `--reseed`.
  - **Removed:** `window_hours`, `--hours` and `changed_urls()`.
    `schedule_interval` now defaults to 3600 s. The func path is unchanged,
    but the job ID includes the interval. A project upgrading from 2.3.326
    keeps the old daily job in Redis beside the new hourly one; cancel
    `schedule_submit_changed_*` with `interval=86400` once.
  - `indexnow` is now a package (`urls`, `transport`, `state`, `sweep`); the
    public names import from it as before.

### Fixed

- **API datetimes were shifted by the visitor's UTC offset while labelled
  `Z`.** `REST_FRAMEWORK["DATETIME_FORMAT"]` is `%Y-%m-%dT%H:%M:%SZ` (literal
  `Z`), but DRF converts an aware datetime to the *active* timezone before
  formatting, and `TimezoneMiddleware` activates the visitor's zone from
  `X-Timezone` (the generated TS SDK sends it). A visitor at +08:00 got local
  wall-clock time marked as UTC: `expires_at` 8 hours late, timers firing 8
  hours late. Plain curl without the header was correct, a browser was not.
  - Fix: `DateTimeField.to_representation` now renders under
    `timezone.override(UTC)`. The wire format is unchanged (literal `Z`).
  - Chosen over a serializer/base-class override because patching DRF's own
    `DateTimeField` covers plain `serializers.DateTimeField()`, ModelSerializer
    fields and subclasses with no project changes. It is applied when
    `django_cfg.middleware.timezone` is imported (that is, whenever the
    middleware is installed); `AppConfig.ready` is not used because
    `django_cfg/apps/` shadows `apps.py`, so `ready()` never runs.
  - Not changed: `TimezoneMiddleware` still activates the zone for templates,
    admin and ORM-side code. Input parsing is untouched, so a naive datetime
    in a request body is still read as visitor-local. A field with an explicit
    `default_timezone=` keeps it.
  - Visible effect: clients that worked around the shift will now show
    correct times; clients that did not were showing wrong ones.
- **A schedule removed from the config no longer keeps firing.** rq-scheduler
  keeps a job until something cancels it. Before this fix a dropped
  `RQScheduleConfig` stayed in Redis, and once its function was deleted it
  raised an ImportError on every run. Registration now records the schedule
  IDs it registered in a per-project Redis set. On the next start it cancels
  any ID in that set that is no longer configured. Jobs enqueued from code,
  and jobs registered by another project on the same Redis DB, are never in
  the set, so they are never touched. Schedules registered before this
  release are not in the set yet; cancel those by hand once.
- **DRF throttles keyed on raw X-Forwarded-For.** Generated `REST_FRAMEWORK`
  now defaults `NUM_PROXIES` to `0` while `RealIPMiddleware` is in
  `MIDDLEWARE`, so `get_ident` returns the resolved `REMOTE_ADDR`. With `None`,
  DRF returned the whole XFF string (`client,edge`) and one client spread over
  a bucket per Cloudflare edge. An explicit `NUM_PROXIES` is kept. Per-project
  `get_ident` overrides that return `REMOTE_ADDR` are no longer needed.

## [2.2.x] — 2025-10 → 2026-07 (consolidated)

> Changelog maintenance resumed at 2.2.95. The gap since 1.2.25 spans the
> whole 2.x line; its user-facing highlights are consolidated here rather
> than reconstructed per release.

### Added
- **Typed API client generation**: TypeScript, Python, and Go clients emitted
  from the live DRF OpenAPI schema (`python manage.py gen`), with grouped
  clients via `OpenAPIGroupConfig`.
- **Config-gated built-in apps**: `currency` (exchange rates + RQ schedule)
  and `geo` (countries/states/cities with select2/nearby/geocode API).
- **Accounts**: `UserAPIKey` manager seam with non-rotating reveal endpoint,
  TOTP app, webmail provider mapping for magic-link UX.
- **Modules**: MCP server for AI assistants, gRPC services (optional HTTP/3
  frontend via `[grpc-h3]`), Centrifugo integration, OG-image rendering,
  sitemap, frontend monitor ingest, admin dashboard tabs, LLM utilities
  (structured output with validate-and-repair, OpenRouter registry).
- **Encryption**: AES-256-GCM response encryption helpers.

### Changed
- Packaging modernized: 15 `requirements-*.txt` files consolidated into
  `pyproject.toml` extras; pytest/pyright/bandit configs consolidated into
  `pyproject.toml`; Python 3.12+ / Django 5.2+ floors.
- Old payment-provider prototype (NowPayments/Cryptomus era) retired to
  archived development logs; superseded by the new payments engine above.

### Removed
- Streamlit support (dead code, package-wide).

### Security
- Dependency floors track 2026 CVE fixes (Django 5.2.14, simplejwt 5.5.1,
  requests 2.33, lxml 6.1, aiohttp 3.13.4, cryptography 46.0.7, and others —
  see comments in `pyproject.toml`).
- Leaked-secret redaction pass; vulnerability reports moved out of the
  package tree.

## [1.2.25] - 2025-09-24

### Added
- **Payment System Enhancements**: Unified payment provider configurations
  - New `PaymentsConfig` model with provider-specific settings
  - Enhanced validation utilities for API keys and subscription access
  - Improved webhook handling and reliability
  - Support for multiple payment providers (NowPayments, Cryptomus, etc.)
- **Template System**: Enhanced project template management
  - Improved template extraction and project name replacement
  - Better integration with CLI `create-project` command
  - More reliable template archiving system

### Changed
- **Project Structure**: Reorganized template location
  - Moved Django sample project to `examples/django_sample`
  - Improved template packaging for better distribution
- **Dependencies**: Updated dependency management
  - Better version constraint handling
  - Improved package compatibility

### Fixed
- **Payment Validation**: Enhanced security for payment processing
  - Improved API key validation
  - Better webhook verification
  - Fixed subscription access control issues
- **CLI Tools**: Improved reliability of project creation
  - Fixed template extraction issues
  - Better error handling for project setup
  - Improved project name replacement logic

### Security
- **Payment Processing**: Enhanced security measures
  - Stronger API key validation
  - Improved webhook verification
  - Better access control for subscription features

## [Previous Versions]

### [1.2.24] and earlier
- Core Django-CFG functionality
- Basic payment provider support
- Configuration management system
- CLI tools for project creation
- Health monitoring modules
- Database and Redis integration

---

**Note**: This changelog focuses on user-facing features and API changes in the Django-CFG package.
