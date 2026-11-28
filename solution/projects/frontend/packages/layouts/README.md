<div align="center">

![@djangocfg/layouts](https://raw.githubusercontent.com/markolofsen/assets/main/libs/djangocfg/layouts.webp)

</div>

# @djangocfg/layouts

Layouts, app shell, and providers for **Next.js App Router**. Part of **[DjangoCFG](https://djangocfg.com)**.

```bash
pnpm add @djangocfg/layouts
```

```css
/* Golden path — bundles Tailwind + tokens + base + utilities, layer-safe */
@import "@djangocfg/ui-core/styles/full";
@import "@djangocfg/layouts/styles";
```

Peers: `@djangocfg/ui-core`, `@djangocfg/api`, `@djangocfg/realtime`, `@tanstack/react-query` 5, React 19,
Next.js 16+, Tailwind CSS 4. List each one in every app that mounts `BaseApp`, so the page holds one copy.

---

## Quick start

Two responsibilities, kept separate:

1. **Providers** — mount `BaseApp` ONCE at the app root (theme, the React
   Query client, auth, i18n, realtime, monitor, toasts). It's framework-agnostic
   (works in Wails/Vite too).
2. **Per-section shell** — each Next.js **route-group `layout.tsx`** imports the
   matching shell (`PrivateLayout` / `PublicLayout`) and passes its own config.
   No runtime layout-router, no `enabledPath` matching.

```tsx
// app/[locale]/layout.tsx — providers, once
import { BaseApp } from '@djangocfg/layouts';
<BaseApp project="my-app" theme={{ defaultTheme: 'system' }}
         auth={{ apiUrl: '…', routes: { auth: '/auth' } }}
         i18n={{ locale, locales, onLocaleChange: changeLocale, routing }}>
  {children}
</BaseApp>

// app/[locale]/(pages)/private/layout.tsx — the private shell
import { PrivateLayout } from '@djangocfg/layouts';
<PrivateLayout sidebar={sidebar} header={header}>{children}</PrivateLayout>
```

See the [**BaseApp README**](./src/layouts/AppLayout/README.md) for the full
provider surface and the Next.js vs Wails wiring, and the demo app
(`apps/demo/app/_layouts`) for a complete reference.

> **Pass `i18n`** when using `next-intl` or any locale-prefixed routing, so the
> link bridge and locale switcher resolve correctly.

---

## Layouts

| Component | Use | Docs |
|---|---|---|
| **`PublicLayout`** | Marketing / docs. Slots for navbar (`Floating`/`Flush`/`Minimal`) + footer + locale + auth controls. | [README](./src/layouts/PublicLayout/README.md) |
| **`PrivateLayout`** | Authenticated app shell — sidebar (collapsible icon rail, accordion groups, rail/featured/CTA slots) + popover account footer. | [README](./src/layouts/PrivateLayout/README.md) |
| **`AuthLayout`** | Sign-in / sign-up flows. Shell-based: `centered` (default) or `split` (two-column desktop). | [README](./src/layouts/AuthLayout/README.md) |

> **Admin** is not a separate layout — use `PrivateLayout` with an admin `sidebar`
> config in your `app/.../admin/layout.tsx`.

### Staff-only route groups

`PrivateLayout`'s guard checks the session. For a surface that also requires
staff, add `requireStaff` (resolved from `useAuth().isAdminUser`, the
`is_staff || is_superuser` fold):

```tsx
<PrivateLayout sidebar={sidebar} header={header} requireStaff>{children}</PrivateLayout>
```

A signed-in non-staff user gets `ForbiddenState` instead of the shell — **not a
redirect to the auth form**: they are already signed in, so signing in again
cannot grant the privilege, and since the guard saves the current URL first, a
redirect would loop back here. Pass `forbiddenFallback` to supply your own
screen. Details: [PrivateLayout README](./src/layouts/PrivateLayout/README.md).

### `AuthLayout` shells

Two visual variants, switchable via the `variant` prop:

- **`centered`** — Apple HIG-style: frameless, centered form, animated glow background.
- **`split`** — Two-column card on desktop (form left, customizable sidebar right); single-column on mobile. Background image/gradient with overlay + blur via the `background` prop.

```tsx
// Split variant with background image and testimonial sidebar
<AuthLayout
  variant="split"
  background={{ imageUrl: '/bg.jpg', overlay: 'hsl(var(--background) / 0.6)', blur: '8px' }}
  sidebar={<Testimonial />}
>
  {/* optional custom header, shown only on identifier step */}
</AuthLayout>
```

Architecture: `AuthShell` orchestrator dispatches to `CenteredShell` or `SplitShell`. Add new variants by extending `AuthShellVariant` and creating a new shell component.

### `ProfileLayout`

```tsx
<ProfileLayout enable2FA enableDeleteAccount tabs={tabs} slots={slots} />
```

| Prop | Role |
|---|---|
| `enable2FA` | Show Security tab with 2FA management. |
| `enableDeleteAccount` | Show Delete account in `⋯` menu. |
| `tabs` | Extra `ProfileTab[]` appended after built-ins. |
| `slots.headerBadge` / `headerMenuItems` / `headerAfter` / `footer` | Slot content around the avatar row, menu, and tab body. |

---

## Theme

Themes are selected by the host application's CSS import. `BaseApp` owns only
the light/dark class and does not inject token styles at runtime:

```css
@import "@djangocfg/ui-core/styles/full";
@import "@djangocfg/ui-core/styles/presets/macos";
```

The package exports `ThemeStylePresetId` and `THEME_STYLE_PRESET_ORDER` for
metadata and selectors. Preset tokens live exclusively in the static CSS
files shipped by `@djangocfg/ui-core`.

---

## i18n

```tsx
import { useLocaleSwitcher } from '@djangocfg/nextjs/i18n/client';
import { routing } from '@djangocfg/nextjs/i18n/routing';

const { locale, locales, changeLocale } = useLocaleSwitcher();
<BaseApp i18n={{ locale, locales, onLocaleChange: changeLocale, routing }}>...</BaseApp>
```

When `routing` is set, `BaseApp` mounts a locale-aware `<Link>` adapter so every layout-rendered link keeps the active locale prefix. Drop it for default-locale-only apps.

With two or more `locales`, `BaseApp` also offers the visitor their browser's language once, quietly ([`LocaleSuggestion`](src/components/LocaleSuggestion/README.md)); `i18n.suggestion: false` turns it off.

---

## Monitor & debug

`baseApp.project` enables `window.monitor`. Debug panel: `Cmd+D` or `?debug=1`.

### `MonitorBoundary`

Error boundary that automatically reports caught errors to `@djangocfg/devtools`. Use at page/layout level so unexpected render errors land in your backend dashboard.

```tsx
import { MonitorBoundary } from '@djangocfg/layouts';

export default function Layout({ children }) {
  return (
    <MonitorBoundary variant="fullscreen" name="root-layout">
      {children}
    </MonitorBoundary>
  );
}

// Per-section, non-fatal:
<MonitorBoundary variant="card" name="dashboard-stats" resetKeys={[pathname]}>
  <StatsPanel />
</MonitorBoundary>

// Opt out of reporting (e.g. third-party iframe noise):
<MonitorBoundary reportToMonitor={false} variant="silent">
  <EmbeddedWidget />
</MonitorBoundary>
```

Wraps `Boundary` from `@djangocfg/ui-core` — same `variant`/`fallback`/`resetKeys` API, plus auto `FrontendMonitor.capture(...)`.

> **One top-level boundary.** `BaseApp` already mounts the app-wide crash
> boundary (UiProviders' built-in one, fed an i18n fallback) — don't wrap a
> second one around the whole app. Use `MonitorBoundary` for **per-section**
> isolation (so one panel's crash doesn't take the page), not as a duplicate
> root boundary. All boundaries share the single ui-core `Boundary` catch.

For local UI widgets that should not report to backend, use `Boundary` from `@djangocfg/ui-core` directly.

## React Query

`BaseApp` owns the page's one QueryClient. The generated hooks of `@djangocfg/api` and of an app's own client use
it; an app mounts no provider of its own.

- A `queryClient` prop wins and is used as it is (its defaults are not merged).
- Else a QueryClient already provided above `BaseApp` is reused, never nested.
- Else `createAppQueryClient()` makes one per mount (`useState`), never at module scope. Defaults: no retry on a 4xx
  or a non-network error, up to 2 on a network error or a 5xx (`shouldRetryQuery`), `throwOnError: false`,
  `staleTime` 30 s, refetch on focus, mutations not retried.
- `queryDevtools={() => import('@tanstack/react-query-devtools')}` mounts React Query Devtools in development only,
  loaded on demand. The app installs the package.

```tsx
import { BaseApp } from '@djangocfg/layouts';
import type { ReactNode } from 'react';

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <BaseApp project="my-app" queryDevtools={() => import('@tanstack/react-query-devtools')}>
      {children}
    </BaseApp>
  );
}
```

`createAppQueryClient` and `shouldRetryQuery` are exported for an app that builds its own client with the same
defaults, for example in tests. There is no SWR in layouts: no `swr` prop, no `SWRConfig`, no SWR peer.

## Realtime

`BaseApp` mounts `RealtimeProvider` from `@djangocfg/realtime` inside the QueryClient and `AuthProvider`. It opens no
socket until something subscribes, so a page that never subscribes costs nothing. The socket URL is the API origin
plus `/ws` (`ws:`/`wss:` by scheme).

- **REST refresh, no code.** A generated query whose view is marked `@invalidated_by("topic")` carries the concrete
  topic names in `meta.realtimeTopics` (`REALTIME_META_KEY`). `BaseApp` watches the QueryCache: while such a query
  has an observer its topics stay subscribed, and a message, a gap or a fresh subscription going live invalidates
  the queries tagged with that topic, once per burst. `topicsOfQuery(query)` reads the tags.
- **Events.** `useTopic(topic, onEvent)` from `@djangocfg/realtime/react` for data pushed in the event itself.
- **Gaps.** Unless `realtime.onGap` is set, a gap on a `useTopic` subscription invalidates the queries tagged with
  that topic too.
- **Issues** (a 4401/4403/4500 close, five failed handshakes in a row, a refused topic, a protocol error, a dev
  schema failure) go to `@djangocfg/devtools` like any other frontend error; normal drops are not reported.

`realtime={{ url, path, onGap, onIssue }}` tunes it, `realtime={false}` removes it. A QueryClient passed explicitly to
a generated hook (its second argument) is a second cache that this bridge never sees. Usage:
[`@djangocfg/realtime`](../realtime/README.md).

## Analytics and auth funnels

`BaseApp` mounts the first-party `AnalyticsProvider` once and bridges events
from `@djangocfg/api/auth`. `AuthLayout` adds a small `layouts.auth.step_viewed`
breadcrumb at each visible step; the server-confirmed `auth_login_success`
event remains the conversion source of truth.

For a custom product goal, use `useAnalytics().event(name, props)` from
`@djangocfg/analytics`. See that package's README for the typed event catalog,
browser facade, and extension pattern. Do not create a second route listener or
send analytics directly from a layout.

---

## Snippets

Small surfaces a host mounts once, exported from `@djangocfg/layouts` and `@djangocfg/layouts/snippets`:

| Export | What |
|---|---|
| `AuthDialog`, `useAuthDialog` | The global sign-in dialog. `BaseApp` mounts it with `auth` enabled; anything can open it, including a widget that only has `dialogStore`. |
| `TwoFactorSetup` | Enrol flow for a settings page: QR, confirmation code, backup codes. |
| `TwoFactorChallengeDialog` | The code prompt that opens over the page when a sign-in step needs 2FA. `AuthLayout` mounts it. |
| Analytics | Re-exported from `@djangocfg/analytics` for older imports; new code imports that package (see Analytics above). |
| `Breadcrumbs` | Breadcrumbs from `items`, or from the current path when none are given. |

## Concepts and decisions

How the layouts fit together (scroll model, safe-area tokens, PWA/mobile behaviour, decision log): [`@docs/`](./@docs/README.md).

## Stories and tests

`@djangocfg/layouts/testing` is for Storybook and tests only: `MockAuthProvider` and `buildMockUser` give `useAuth()` a fixed session, `MockAuthFormProvider` and the step components mount a sign-in step without the full `AuthLayout`. Do not import it from production code.

---

## Package exports

| Path | Contents |
|---|---|
| `@djangocfg/layouts` | Barrel. |
| `@djangocfg/layouts/layouts` | Layout components. |
| `@djangocfg/layouts/snippets` | `AuthDialog`, the 2FA surfaces, `Breadcrumbs`, `Devtools`, the analytics re-export. |
| `@djangocfg/layouts/components` | Misc + `ErrorLayout`, `RedirectPage`. |
| `@djangocfg/layouts/utils` | Path matching and sidebar-navigation helpers, logger. |
| `@djangocfg/layouts/pages` | Page templates (`legal`). |
| `@djangocfg/layouts/configurator` | JSON Schemas for `<JsonSchemaForm>`-driven configurator UIs. Pair with `@djangocfg/widget-forms`. |
| `@djangocfg/layouts/configurator/private` | The `PrivateLayout` configurator schema on its own. |
| `@djangocfg/layouts/testing` | Storybook and test helpers; not for production code. |
| `@djangocfg/layouts/styles` | Base CSS. |
| `@djangocfg/layouts/styles/dashboard` | Dashboard shell CSS. |

Extensions: `@djangocfg/ext-newsletter`, `ext-knowbase`, `ext-leads`, `ext-payments`, `ext-support`, …

## License

MIT — [DjangoCFG](https://djangocfg.com)
