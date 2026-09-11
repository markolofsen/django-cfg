---
title: "@djangocfg/layouts"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# `@djangocfg/layouts`

App shell and providers for the Next.js App Router. Two responsibilities, kept
separate — conflating them is the usual mistake.

| Export | Role |
|---|---|
| `BaseApp` | **Providers.** Theme, auth, i18n, SWR, monitor, toasts. Mount **once** at the app root. |
| `PublicLayout` | Marketing / public shell: navbar slots (`Floating` / `Flush` / `Minimal`), footer, locale and auth controls |
| `PrivateLayout` | Authenticated shell: collapsible sidebar rail, accordion groups, popover account footer |
| `AuthLayout` | Sign-in / sign-up. `variant="centered"` (default) or `"split"` |
| `SettingsLayout` | Settings sections |
| `MonitorBoundary` | Error boundary that reports to `@djangocfg/devtools` |
| `RedirectPage` | A page that only redirects |
| `LocaleSwitcher`, `UserMenu`, `UserAvatar` | Shell pieces, usable standalone |

There is **no `ProfileLayout`** and no separate admin layout, despite what the
upstream README says. Admin is `PrivateLayout` with an admin `sidebar` config.

## How this workspace mounts it

`BaseApp` lives in `apps/*/app/providers.tsx`, once per app. `AuthLayout` is used
directly by `apps/*/app/(auth)/auth/page.tsx`.

```tsx
// app/[locale]/layout.tsx — providers, once
<BaseApp project="…" theme={{ defaultTheme: "system" }}
         auth={{ apiUrl: "…", routes: { auth: "/auth" } }}
         i18n={{ locale, locales, onLocaleChange: changeLocale, routing }}>
  {children}
</BaseApp>

// app/[locale]/(pages)/private/layout.tsx — the shell, per route group
<PrivateLayout sidebar={sidebar} header={header}>{children}</PrivateLayout>
```

**The shell goes in a route-group `layout.tsx`, not inside a page.** There is no
runtime layout-router and no `enabledPath` matching — the route group *is* the
selector.

## Traps

- **`BaseApp` twice is the bug, not the fix.** It mounts the Tooltip / Dialog /
  Toast providers; a second instance gives two `createContext()` identities and
  produces `Tooltip must be used within TooltipProvider` from a component that
  looks correctly nested.
- **Pass `i18n` whenever routing is locale-prefixed.** With `routing` set,
  `BaseApp` mounts a locale-aware `<Link>` adapter so every shell-rendered link
  keeps its locale prefix. Without it links silently drop the prefix.
- **`@import "@djangocfg/layouts/styles"` is required**, after
  `ui-core/styles/full`. See [ui-core styling](ui-core-styling.md).
- **Themes come from the host's CSS import**, not from `BaseApp`. It owns the
  light/dark class only and injects no tokens at runtime.

`baseApp.project` enables `window.monitor`; the debug panel opens on `Cmd+D` or
`?debug=1`.
