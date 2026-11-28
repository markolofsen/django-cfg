# BaseApp — provider stack

`BaseApp` is the **single, framework-agnostic provider wrapper** for any React
host. It mounts theme, auth, i18n, the React Query client, realtime, error tracking, monitor, the debug
panel, and the router adapter — everything an app needs *above* the page tree.

There is **no `AppLayout` layout-router** anymore. Picking which shell
(public / private / admin) wraps a route is the job of **native Next.js
route-group `layout.tsx` files**, not a runtime path-matcher. This is simpler,
RSC-friendly, and supports per-segment `loading.tsx` / `error.tsx`.

## Where it goes

### Next.js — mount once at the app root

```tsx
// app/[locale]/layout.tsx  (or app/layout.tsx)
import { BaseApp } from '@djangocfg/layouts';

export default function RootLayout({ children }) {
  return (
    <html><body>
      <BaseApp
        project="my-app"
        theme={{ defaultTheme: 'system', storageKey: 'myapp-theme' }}
        // Public app with no login: auth={false} apiUrl={process.env.NEXT_PUBLIC_API_URL}
        auth={{ apiUrl: process.env.NEXT_PUBLIC_API_URL,
                routes: { auth: '/auth', defaultCallback: '/private' } }}
        // devtools ingest uses auth.apiUrl, or `apiUrl` when auth={false}, as its base URL
        // analytics / monitor / errorTracking / debug — all optional
      >
        {children}
      </BaseApp>
    </body></html>
  );
}
```

Then each section owns its shell via a route-group layout:

```tsx
// app/[locale]/(pages)/private/layout.tsx
import { PrivateLayout } from '@djangocfg/layouts';
export default function PrivateRouteLayout({ children }) {
  return <PrivateLayout sidebar={sidebar} header={header}>{children}</PrivateLayout>;
}

// app/[locale]/(marketing)/layout.tsx
import { PublicLayout } from '@djangocfg/layouts';
export default function PublicRouteLayout({ children }) {
  return <PublicLayout navbar={<MyNavbar/>} footer={<MyFooter/>}>{children}</PublicLayout>;
}
```

`/auth/*` and other fullscreen pages just live outside those groups — no
`noLayoutPaths` config needed; they simply aren't wrapped.

> **Admin** is not a separate layout — it's `PrivateLayout` with a different
> `sidebar` config in `app/.../admin/layout.tsx`.

### Non-Next.js (Wails / Electron / Vite / plain React)

`BaseApp` does not depend on Next routing — use it directly as the top-level
wrapper. This is exactly how the Wails desktop app mounts the framework.

```tsx
import { BaseApp } from '@djangocfg/layouts';

export function App() {
  return <BaseApp project="desktop" theme={{ defaultTheme: 'dark' }}>{routes}</BaseApp>;
}
```

## Config surface

```ts
// BaseAppProps = BaseLayoutProps (src/layouts/types/layout.types.ts), abridged
interface BaseAppProps {
  children: ReactNode;
  project?: string;            // devtools project + debug panel title default
  theme?: ThemeConfig;         // defaultTheme, storageKey
  auth?: AuthConfig | false;   // false = no AuthProvider (fully public app); `{ sso: true }` = one sign-in host (auth.<apex>) for the subdomains
  apiUrl?: string;             // API origin for devtools and realtime when auth={false}
  analytics?: AnalyticsConfig; // Google Analytics
  errorTracking?: ErrorTrackingConfig;
  queryClient?: QueryClient;   // the app's own; else one above BaseApp is reused, else one with our defaults
  queryDevtools?: QueryDevtoolsLoader; // () => import('@tanstack/react-query-devtools'), dev builds only, lazy
  errorBoundary?: ErrorBoundaryConfig; // enabled by default
  devtools?: DevtoolsConfig;   // capture, ingest, debug panel
  realtime?: RealtimeConfig | false; // lazy WebSocket; issues go to devtools; false removes it
  i18n?: I18nLayoutConfig;     // locale + routing for the link bridge
  pwaMeta?: boolean;           // installed-app meta tags, on by default
  progressBar?: boolean | RouteProgressOptions;
  debug?: boolean;             // the viewport diagnostic dot
}
```

## React Query and realtime refresh

`BaseApp` owns the page's one QueryClient (`query/AppQueryProvider.tsx`):

- a `queryClient` prop wins and is used as it is, its defaults unmerged;
- else a QueryClient already provided above `BaseApp` is reused, so a page never holds two caches;
- else `createAppQueryClient()` makes one per mount (`useState`), never at module scope.

Its defaults: no retry on a 4xx or a non-network error, up to 2 on a network error or a 5xx (`shouldRetryQuery`),
`throwOnError: false`, `staleTime` 30 s, refetch on focus, and mutations are not retried. `queryDevtools` renders
React Query Devtools in development builds only, loaded lazily; the app installs `@tanstack/react-query-devtools`.
`@tanstack/react-query` is a peer: every app that mounts `BaseApp` lists it. There is no SWR here.

A generated query whose view is marked `@invalidated_by("topic")` carries the
concrete topic names in `meta.realtimeTopics` (the generated
`runtime/realtime-query.ts`). `RealtimeMount` (`realtime/queryRealtime.ts`,
`bridgeQueryCache`) watches the QueryCache. While such a query has an observer,
its topics stay subscribed (released lazily, 1.5 s after the last one goes). A
message, a gap or a fresh subscription going live invalidates the queries tagged
with that topic. The page needs no code. A QueryClient passed to a hook as its
second argument is not this cache, and its queries never refresh this way.

## Per-route forced theme (optional)

To force a theme on a subtree (e.g. an always-dark marketing landing) without
locking the whole app, wrap that route-group's layout with `<ThemeOverride>` /
`<ForceTheme>` (re-exported here from `@djangocfg/ui-core/theme`). Because shell
selection is now per route-group, the override lives right where the route does.

## Related

- `PrivateLayout` / `PublicLayout` — the per-section shells (see their READMEs).
- `ErrorLayout` (`@djangocfg/layouts/components`) — universal error page for
  `error.tsx` / `not-found.tsx`.
- `ForceTheme` / `ThemeOverride` (`@djangocfg/ui-core/theme`) — theme primitives.
