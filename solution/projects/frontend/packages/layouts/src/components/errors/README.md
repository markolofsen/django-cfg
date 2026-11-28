# Errors — boundaries + runtime error tracking

In-app error surfacing for `@djangocfg/layouts`: React error boundaries, a global
runtime error tracker, and developer-facing toasts (with a Copy-as-cURL action).

## Pieces

All boundaries here build on the single `Boundary` primitive in
`@djangocfg/ui-core` — no duplicate catch logic. `BaseApp` mounts ONE boundary
(UiProviders' built-in, fed an i18n fallback), so apps don't wrap their own.

| File | What it does |
|------|--------------|
| `AppErrorFallback.tsx` | The one localized crash screen: title, text, support email, ONE "Refresh Page" button (hard reload). Used by `BaseApp` and `ErrorBoundary`. |
| `ErrorBoundary.tsx` | Thin wrapper over ui-core `Boundary` — renders `AppErrorFallback` (for direct use; `BaseApp` no longer wraps it). |
| `MonitorBoundary.tsx` | ui-core `Boundary` that also reports to `@djangocfg/devtools`. |
| `ErrorLayout.tsx` | Full-page error layout (`getErrorContent` / `ERROR_CODES`). |
| `ErrorsTracker/` | Global runtime tracker — listens for error CustomEvents and shows toasts. |

## Stale chunks after a deploy

A chunk-load failure (ChunkLoadError, "Loading chunk N failed", dynamic import failure, cancelled fetch of `/_next/static/...`) is a stale tab, not a crash: the page reloads ONCE instead of showing the error screen. Logic lives in `@djangocfg/ui-core/lib` (`chunk-reload.ts`), wired in `Boundary` (render errors), `UiProviders` (window `error` + `unhandledrejection`) and `ErrorLayout error={error}` (`global-error.tsx`). Loop guard: `sessionStorage` key `djangocfg:chunk-reload-at`, 30 s window; with storage blocked no auto reload. Tests: `chunkReload.test.ts`, `AppErrorFallback.test.tsx`.

## ErrorLayout — `statusUrl`

`ErrorLayout` takes an optional `statusUrl`, rendered as a secondary link beside
the support line (`layouts.errors.checkStatus`). It answers the question a 500
actually raises — *is it me or is it them?*

```tsx
<ErrorLayout code={500} supportEmail={…} statusUrl="https://status.example.com" />
```

There is **no default**: this package is generic, so the URL belongs to the
consuming product. Omit it and the link does not render.

Two rules:

- **Server faults only** (500/502/503/504, `global-error`). Never on a 404 —
  sending someone who mistyped a URL to check for an outage is noise, and it
  teaches people to ignore the link when it matters.
- **Never fetch it to show status inline.** An error page renders when the
  infrastructure is already unhealthy, so that request is the least likely to
  succeed — and a failed one would either reassure falsely or raise a second
  error inside the first. A link always works.

This is a *user-facing recovery* path. `ErrorsTracker` below is the
*developer-facing debugging* path. Different audiences — keep them apart.

## ErrorsTracker

`ErrorTrackingProvider` listens on `window` for typed error events dispatched by
the generated API client and runtime, then renders a Sonner toast per error.

Tracked error types: `validation` (zod response mismatch), `network` (failed/4xx/5xx
requests, incl. a CORS heuristic), and `runtime` (uncaught JS).

```tsx
import { ErrorTrackingProvider } from '@djangocfg/layouts'; // (or the module path)

<ErrorTrackingProvider
  validation={{ enabled: true }}
  network={{ enabled: true, showStatusCode: true }}
>
  {children}
</ErrorTrackingProvider>
```

### Toast actions

Each toast has **Copy error** (JSON to clipboard) and, for requests, **Copy cURL**.

### Copy-as-cURL

`utils/curl-generator.ts` builds a runnable cURL from the failed request, with
`Authorization: Bearer <token>` (read live via `auth.getToken()`), so the command
works as-is in a terminal.

## Notes

- The `isDev` flag comes from `@djangocfg/ui-core/lib`.
- Errors also flow to `@djangocfg/devtools` (backend ingest + debug panel) for
  inspection regardless of toast visibility.
