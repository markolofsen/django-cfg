# @djangocfg/demo

Minimal Next.js shell wired to `django-cfg` — the smallest app that
shows how all the framework pieces fit together. UI primitives,
component variants, and interaction demos live in
[`apps/storybook`](../storybook); this app is intentionally **not** a
component showcase.

## What this demonstrates

- App shell via `BaseApp` from `@djangocfg/layouts` (theme + i18n + auth wiring).
- `next-intl` routing with `en` / `ru` / `ko`, merging
  `@djangocfg/i18n` base translations with app-specific ones.
- Auth-gated `/private` and admin-gated `/admin` route groups,
  built on `useAuth()` from `@djangocfg/api/auth`.
- The drop-in sign-in flow from `<AuthLayout />` in `@djangocfg/layouts`.
- `sitemap.ts` / `robots.ts` / `manifest.ts` via `@djangocfg/nextjs`
  helpers — same pattern as `apps/vamcar`.

## Page map (5–10 pages)

```
/                      → public landing
/auth                  → sign-in (AuthLayout from @djangocfg/layouts)
/realtime              → live topics against apps/realtime_demo (Django ASGI on :8000)
/private               → dashboard       ─┐
/private/profile       → account fields    │  guarded by useAuth()
/private/settings      → theme + locale   ─┘
/admin                 → redirects to /admin/users
/admin/users           → admin example    ─ guarded by is_staff
/legal/privacy         → placeholder
/legal/terms           → placeholder
```

## Run

```bash
cp .env.example .env.local        # set NEXT_PUBLIC_API_URL to your Django host
pnpm install
pnpm --filter @djangocfg/demo dev # http://localhost:3010
```

## Single sign-in host (optional)

The demo doubles as the reference for the "one sign-in host for the subdomains" setup
(docs → *One sign-in host for subdomains*). It is one switch, `NEXT_PUBLIC_SSO=true`:

| Where it runs | `NEXT_PUBLIC_SITE_URL` | Behaviour |
|---|---|---|
| The sign-in host | `https://auth.example.com` | The form at `/auth`; after sign-in it returns the visitor to a validated `?next=`. Never redirects, needs no session. |
| Any other app of the family | `https://my.example.com` | No form: a signed-out visitor of `/private` or `/admin` goes to `https://auth.example.com/auth?next=<page>` (the proxy does it before render) and is sent back. |
| `localhost` | `http://localhost:3010` | No common domain, so SSO is off and the demo uses its own `/auth` as before (one console line). |

That is all the app code: `auth={{ sso: true }}` in [`AppLayout`](app/_layouts/AppLayout.tsx) and
`createSsoMiddleware` in [`proxy.ts`](proxy.ts). Everything else (cookie on `.example.com`, the `next` check, the
redirect loop guard) is in `@djangocfg/api` / `@djangocfg/nextjs`. Register one OAuth redirect URI,
`https://auth.example.com/auth?provider=google`.

## Customize

- **Brand / metadata**: `app/_core/settings.ts`
- **Sitemap entries**: `app/sitemap.ts`
- **Disallow rules**: `app/robots.ts`
- **Theme tokens & fonts**: `app/_core/globals.css` (+ `@theme` block)
- **i18n strings**: `i18n/locales/{en,ru,ko}.ts` (add a locale → also
  update `i18n/request.ts`)
- **Routes & private menu**: `app/_routes/{public,private,admin}.ts`

## Not included on purpose

- Component galleries — see [`apps/storybook`](../storybook).
- Generated API clients — wire your own with `make api` from the
  Django project; the demo only consumes the framework auth context.
- Debuger / monitor extras — add them when you actually
  need them; the demo keeps deps thin.
