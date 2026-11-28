# Router hooks

Framework-agnostic navigation primitives for `@djangocfg/ui-core`. Built on plain browser APIs (`window.history`, `window.location`, `URLSearchParams`, `popstate`). No `next/*`, no `react-router`, no third-party deps.

## Surface

| Hook | Purpose |
| --- | --- |
| `useLocation` | Reactive snapshot of `window.location` (`pathname`, `search`, `hash`, `href`). |
| `useNavigate` | Programmatic navigation: `navigate`, `navigateExternal`, `push`, `replace`, `back`, `forward`. |
| `useQueryParams` | Read/write `?key=value` URL state with typed coercion (`get`, `getNumber`, `getBoolean`, `set`, `remove`, `clear`). |
| `useBackOrFallback` | Smart "back" that falls back to a route when there's no in-app history. |
| `useUrlBuilder` | Pure URL/querystring assembly: `build`, `withCurrentParams`. |
| `useSmartLink` | Click + keyboard handlers that turn any element into a proper link (cmd-click, middle-click, Enter, Space). |
| `useIsActive` | `boolean` for "current pathname matches this href" — for nav-item highlighting. |
| `useQueryState` | Typed `useState`-style hook bound to ONE URL key (with parsers + `clearOnDefault`). |
| `useHashState` | `useState`-style hook bound to the URL fragment (`#…`). Writes bypass the adapter — see [`useHashState`](#usehashstate-url-fragment) below. |
| `usePathnameChange` | Callback when the PATH changes (a push, replace, back or forward to another pathname); a query or hash change does not count. For a surface that covers the page and must close on navigation: `usePathnameChange(close, { enabled: open && isMobile })`. `watchPathname` is the non-React core. |
| `useLocationProperty` | Subscribe to ONE derived field of `window.location` (avoids re-renders on unrelated fields). |
| `useRouter` | Convenience facade composing the above. |
| `RouterAdapterProvider` | Swap the navigation backend (e.g. Next.js's router). |
| `useNavigationBehavior` | A page or section switches off the scroll jump and the top loading bar while it is mounted. See [Scroll and loading bar](#scroll-and-loading-bar). |
| `parseAsString` / `parseAsInteger` / `parseAsFloat` / `parseAsBoolean` / `parseAsIsoDate` / `parseAsStringEnum` / `parseAsArrayOf` / `parseAsJson` | Parser builders for `useQueryState`. Each has `.withDefault(value)`. |

## Decomposition rationale

Each atomic hook subscribes to exactly what it needs. A component that only calls `navigate(...)` shouldn't re-render every time the querystring changes — `useNavigate` doesn't subscribe to location, so it doesn't. Same for `useUrlBuilder` (only re-renders on `search` change), `useQueryParams` (same), and so on.

`useRouter` exists for convenience and ergonomic familiarity. Use it when you want everything in one return; use the atomic hooks for fewer re-renders and better tree-shaking.

## Adapter pattern

Default behavior uses `window.history.pushState` + `window.location` and works in any browser (Wails / Electron / Vite / CRA — nothing to mount, it just works).

For Next.js — mount both adapters once near the root. They bridge router hooks to `next/navigation` and `<Link>` to `next/link` so server components, route loaders, and prefetch fire correctly:

```tsx
// app/[locale]/layout.tsx (or wherever your client provider stack lives)
import { NextRouterAdapter, NextLinkProvider } from '@djangocfg/ui-core/adapters/nextjs';

<I18nProvider locale={locale} messages={messages}>
  <NextRouterAdapter>
    <NextLinkProvider>
      {children}
    </NextLinkProvider>
  </NextRouterAdapter>
</I18nProvider>
```

> Using `@djangocfg/layouts`? `BaseApp` already mounts both adapters — you don't
> need this manual wiring.

For a **React-Router v7** SPA (Vite / CRA) — mount the React-Router adapter once,
**inside** the router context (e.g. in the layout-route element, not around
`<RouterProvider>`). It bridges the router hooks to `useNavigate` and `<Link>` to
React-Router's `<Link>`, so ui-core navigation drives the data router instead of
the bare-`pushState` fallback (which would desync the router):

```tsx
// the layout-route element (rendered inside <RouterProvider>)
import { ReactRouterProvider } from '@djangocfg/ui-core/adapters/react-router';

<ReactRouterProvider>
  {/* sidebar / top-bar / <Outlet/> */}
</ReactRouterProvider>
```

`ReactRouterProvider` composes `ReactRouterAdapter` (router hooks) +
`ReactRouterLinkProvider` (`<Link>`); mount either individually if you only need
one. RR's `<Link>` has no `prefetch`-boolean / `scroll` prop, so those ui-core
`<Link>` props are ignored by this adapter (by design).

Both `next` and `react-router` are **optional peer dependencies** — the package
never imports from `next/*` or `react-router` from the main entry. Each adapter
lives behind its own sub-path (`/adapters/nextjs`, `/adapters/react-router`), so a
consumer only pulls in the framework it actually mounts.

For other routers (TanStack Router, wouter, Remix, custom transports) — write a ~20-line custom adapter:

```tsx
'use client';

import { useMemo } from 'react';
import { RouterAdapterProvider, type RouterAdapter } from '@djangocfg/ui-core/hooks';

export function MyRouterAdapter({ children }: { children: React.ReactNode }) {
  const myRouter = useMyRouter();
  const adapter = useMemo<RouterAdapter>(() => ({
    push:    (url) => myRouter.push(url),
    replace: (url) => myRouter.replace(url),
    back:    () => myRouter.back(),
    forward: () => myRouter.forward(),
    getLocation: () => ({
      pathname: window.location.pathname,
      search:   window.location.search,
      hash:     window.location.hash,
    }),
  }), [myRouter]);

  return <RouterAdapterProvider value={adapter}>{children}</RouterAdapterProvider>;
}
```

**Adapter contract gotcha:** custom `push` / `replace` implementations should ultimately route through `window.history.pushState` (Next does, so does react-router). If yours doesn't, dispatch `'djc:navigate'` after each navigation manually so `useLocation` re-reads.

## Scroll and loading bar

`push`/`replace` (and `navigate`) take `{ scroll?, progress? }`, and the Next adapter honours both:

| Option | Absent | `true` | `false` |
| --- | --- | --- | --- |
| `scroll` | the page's setting, then `NextRouterAdapter defaultScroll`, then Next's own default | scroll to the top | keep the position |
| `progress` | the bar shows only when the **pathname** changes; `?query` and `#hash` changes never show it | show it | do not show it |

`useQueryState` passes `scroll: false` and `progress: false` by default (it only ever changes the query); both can be set on the hook or on a single `setValue` call.

A page that navigates inside itself (filters, a board, threads) declares it once instead of on every call, and it also covers `<Link>` clicks and `useScrollToTop`:

```tsx
useNavigationBehavior({ scroll: false, progress: false }); // while this component is mounted
```

Later or nested entries win field by field; an explicit option on a call beats the page. `BaseApp progressBar={false}` removes the bar for the whole app; `progressBar={{ shouldShow: (from, to) => ... }}` replaces the default route rule. `<Link scroll={false}>` is still how a single link keeps Next's scroll.

The bar is ours: [`route-progress`](../../route-progress/README.md). The adapter starts it for programmatic navigation, link clicks are caught by the provider, and every committed navigation (a new pathname, or Next's `pushState`) ends it, with a 15 s ceiling, so a forced bar on a query change cannot hang. Without a `RouteProgressProvider` above (BaseApp mounts one) there is no bar and `useNavigationBehavior` does nothing.

## Shallow writes (no navigation)

`useQueryState(key, parser, { shallow: true })`, or `setValue(v, { shallow: true })` for one call, writes the URL through the History API and nothing else: no request to the server, no server components re-rendered, no loading bar, no scroll (`scroll` and `progress` are ignored). For state only the client needs (a view mode, a zoom, a slider), above all on `force-dynamic` pages where every router call is a full server render. Precedence: the call, then the hook, then `false`. `replace` still picks `replaceState` or `pushState`; with `push`, Back and Forward restore the earlier value (`useLocation` listens to `popstate`). `useNavigate().shallow(href, { replace })` is the same write without the hook.

The adapter method is `RouterAdapter.shallow?(url, { replace })`; the default and Next adapters implement it, passing `null` as the history state (Next syncs `useSearchParams` only for entries without its own `__NA`/`_N` keys, so `history.state` must not be forwarded). An adapter without it falls back to `push`/`replace` with the bar and scroll off.

Setters read the URL at the moment of the call, not the one the last render saw, so two calls in one tick both land and a functional updater sees the earlier write (this holds for normal mode too, though there the URL changes only when the router commits).

## `useQueryState` (typed URL state)

Bound to one query key with a typed parser. Inspired by `nuqs` but framework-agnostic via the same adapter context.

```tsx
import {
  useQueryState,
  parseAsInteger,
  parseAsStringEnum,
} from '@djangocfg/ui-core/hooks';

const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
const [tab,  setTab]  = useQueryState('tab',  parseAsStringEnum(['list', 'grid']).withDefault('list'));

setPage((prev) => prev + 1); // functional updater, just like useState
setPage(null);               // clears the key from the URL
```

`scroll` and `progress` (both default `false`) are described in [Scroll and loading bar](#scroll-and-loading-bar). `clearOnDefault` (default `true`) drops the key from the URL when the value equals the parser default — keeps URLs short. Pass `{ clearOnDefault: false }` to keep explicit `?page=1` for shareable links.

Parsers: `parseAsString`, `parseAsInteger`, `parseAsFloat`, `parseAsBoolean`, `parseAsIsoDate`, `parseAsStringEnum([...])`, `parseAsArrayOf(item)`, `parseAsJson<T>()`. Each has `.withDefault(value)`. Build your own by satisfying the `QueryParser<T>` interface — it's three functions (`parse`, `serialize`, `eq`).

## `useHashState` (URL fragment)

`useState`-style binding to `window.location.hash`. The value is the fragment **without** the leading `#` (`''` when absent); setting `''`/`null` strips it.

```tsx
import { useHashState } from '@djangocfg/ui-core/hooks';

const [hash, setHash] = useHashState();
setHash('settings/account');            // → …/private#settings/account (pushState)
setHash('overview', { replace: true }); // no new history entry
setHash((h) => h || 'top');             // functional updater
setHash(null);                          // strip the fragment → …/private
```

**Why it bypasses the adapter (and `useQueryState` does not).** The fragment is the one part of the URL that must NOT go through `navigate()` / `next.push()`:

- The hash is invisible to the server, so a `#hash` change needs no RSC refetch / loader / prefetch — routing it through the framework router is wasteful.
- Worse, it's **wrong** under Next.js App Router: `router.push('/path#b')` where `/path` equals the current pathname resolves the target *relative to the current URL including its existing hash*, so pushing `…#b` while the URL already reads `…#a` yields a doubled `…#a#b` (compounded by `next-intl` locale prefixing).

So `useHashState` writes via `history.pushState` / `replaceState` directly, against the **absolute** URL. Reads stay reactive through the same patched-history observation as every other router hook, so the round-trip works in Next / Wails / Vite / plain React alike.

Query state is the opposite: `?key=value` IS server-visible, so `useQueryParams` / `useQueryState` deliberately go **through** the adapter — a query change must drive Next's router to refetch server components and re-run loaders. Don't "fix" them to use the History API.

## How `useLocation` knows about `pushState`

Browsers don't fire `popstate` for programmatic `pushState` / `replaceState`. We monkey-patch both methods once (idempotent, module-level guard) on first mount and dispatch a custom `'djc:navigate'` event after each call. Anyone calling history APIs anywhere in the page will trigger an update — including the consumer's own router, third-party scripts, and our default adapter.

## SSR

- All hooks return safe defaults on the server (`pathname: '/'`, etc.).
- `useSyncExternalStore`'s `getServerSnapshot` is wired up correctly.
- Mutating methods (`push`, `replace`, `navigate`, `navigateExternal`) no-op when `window` is undefined.
- No hydration mismatches — first client render reads real `window.location` after mount via `useSyncExternalStore`'s `getSnapshot`.

## Trade-offs vs. `next/navigation`

| Concern | `next/navigation` | This library |
| --- | --- | --- |
| Server components fire | yes (built-in) | only if you mount the Next adapter |
| Pending state (`useTransition`) | bundled in | wrap calls yourself |
| Locale-prefix handling | yes | no — wrap if needed |
| Route matching / dynamic segments | yes | no — out of scope |
| Works outside Next | no | yes — anywhere React runs |
| `<Link>` component | yes | yes — `<Link>` / `<ButtonLink>` in `@djangocfg/ui-core/components` (Next-aware via `NextLinkProvider`) |

Out of scope: locale prefixes, route matching, dynamic segments, transitions. Add them in consumer code or in higher-level packages.
