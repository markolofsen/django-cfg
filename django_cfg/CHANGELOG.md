# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
