---
title: "@djangocfg/api, i18n, analytics, devtools"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# `api`, `i18n`, `analytics`, `devtools`

The four remaining dependencies. Each has a small surface here.

## `@djangocfg/api`

The generated Django client, plus auth.

| Subpath | Holds |
|---|---|
| `.` | the client |
| `/auth` | `useAuth` and the auth store |
| `/auth/server` | the server-side half |
| `/clients` | typed clients |
| `/hooks` | SWR hooks |

Used here through `useAuth` from `@djangocfg/api/auth`
(`packages/portal/src/ui/chrome/account-control.tsx`,
`.../ui/operator/inspector.tsx`).

**This workspace also has its own `@mls/api`** — a separately generated client
for the MLS backend, in `packages/api/src/generated/`. They are different
packages against different backends; reaching for the wrong one compiles and then
calls the wrong host.

**The generated store is the only auth engine.** Do not build a second session
layer beside it: it already does fetch-based auto-refresh and public-mode
fallback, and a parallel one produces a UI that hangs on "Authenticating…"
against a blacklisted token.

## `@djangocfg/i18n`

| Subpath | Holds |
|---|---|
| `.` | runtime helpers |
| `/locales`, `/locales/*` | catalogues |
| `/utils` | helpers |
| `/cli` | the translation CLI |

Locale-prefixed **routing** is `@djangocfg/nextjs/i18n/*`, not this package —
see [nextjs](nextjs.md). This one owns the catalogues.

When adding a nested key via the CLI, check the parent block: the CLI edits the
parsed object rather than splicing text, so a nested add no longer duplicates its
parent — but a hand-edited catalogue can still diverge.

## `@djangocfg/analytics`

`.` and `/core`. GA4 pageview transport.

**A pageview layer already exists** in the packages — it auto-tracks via
`react-ga4`. Swap the transport; do not build a second tracker beside it.

**Never send an `application/json` Blob through `sendBeacon`.** It triggers a
CORS preflight that dies on unload while `sendBeacon` still returns `true` — the
data is lost and nothing reports it. Use a same-origin proxy, or accept
`text/plain`.

## `@djangocfg/devtools`

`.`, `/server`, `/styles`. The dev inspector panel; `@import
"@djangocfg/devtools/styles"` is in `globals.css`. Opens on `Cmd+D` or `?debug=1`
when `BaseApp` has a `project`.
