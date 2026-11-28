# Boundary

React error boundary primitive with four visual variants, a `useBoundary()` hook for async errors, and safe-by-default behaviour (no infinite loops, normalized errors, accessible fallbacks).

Designed as a drop-in replacement for `react-error-boundary` with batteries included: built-in fallback variants, dev logging, optional context-based escape hatch.

---

## When to use

| Situation | Component |
|---|---|
| Wrap a non-critical widget (chat launcher, embed, ad) | `<Boundary variant="silent">` |
| Wrap a row / inline block (table cell, list item) | `<Boundary variant="inline">` |
| Wrap a feature panel (analytics card, settings group) | `<Boundary>` (card, default) |
| Wrap an entire screen / root layout | `<Boundary variant="fullscreen">` |
| Page/layout level with backend reporting | `<MonitorBoundary>` from `@djangocfg/layouts` |

**Granularity matters.** One global boundary at the app root hides bugs and ruins UX (whole page = error screen). Prefer many small per-feature boundaries.

---

## Basic usage

```tsx
import { Boundary } from '@djangocfg/ui-core';

<Boundary variant="card" name="dashboard-stats">
  <StatsPanel />
</Boundary>
```

The `name` prop is used in dev console logs — set it to something findable.

---

## Variants

```tsx
<Boundary variant="silent">…</Boundary>      // renders null on error
<Boundary variant="inline">…</Boundary>      // compact one-line alert + Retry
<Boundary variant="card">…</Boundary>        // bordered card with Retry (default)
<Boundary variant="fullscreen">…</Boundary>  // centered fullscreen + Refresh page
```

All visible variants get `role="alert"` and `aria-live="assertive"` so screen readers announce them.

---

## Custom fallback

Two forms — pick by use case:

```tsx
// Render-prop: simple inline cases
<Boundary fallback={({ error, reset }) => <MyError onRetry={reset} />}>…</Boundary>

// Component: better for memoization / testing
function MyFallback({ error, errorInfo, reset }: BoundaryRenderProps) {
  return <ErrorCard message={error.message} onRetry={reset} />;
}
<Boundary FallbackComponent={MyFallback}>…</Boundary>
```

`fallback` (function form) takes precedence over `FallbackComponent`. Both receive `{ error, errorInfo, reset }`.

---

## Reset patterns

### 1. Auto-reset on route change

```tsx
const pathname = usePathname();
<Boundary resetKeys={[pathname]}>{children}</Boundary>
```

When any value in `resetKeys` changes (shallow `Object.is` per index), the boundary clears its error state.

**⚠ Anti-pattern:** `resetKeys={[Math.random()]}` or `resetKeys={[{}, []]}` causes an infinite reset loop because the array contents change on every render.

### 2. React Query / refetch on recovery

```tsx
<Boundary
  onReset={({ reason }) => {
    // reason === 'imperative' (Retry button) or 'keys' (resetKeys changed)
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  }}
>
  <Dashboard />
</Boundary>
```

`onReset` is called in a microtask **after** state is cleared — your refetch sees a fresh component.

### 3. Full remount (rare)

If you need to fully discard component state (not just the error), use React's `key` prop instead:

```tsx
<Boundary key={feature.id} resetKeys={[feature.id]}>…</Boundary>
```

---

## Async / event-handler errors

**React error boundaries do not catch async errors.** That's a React limitation, not a bug.

Use `useBoundary()` to push them into the nearest boundary:

```tsx
import { useBoundary } from '@djangocfg/ui-core';

function LoadButton() {
  const { showBoundary, resetBoundary } = useBoundary();

  return (
    <Button onClick={async () => {
      try {
        await api.loadData();
      } catch (err) {
        showBoundary(err);  // bubbles up to the closest <Boundary>
      }
    }}>
      Load
    </Button>
  );
}
```

`useBoundary()` works inside any component rendered under a `<Boundary>`. Throws if used outside one.

---

## Logging

By default, caught errors are logged with `console.error` in development and silenced in production. Wire to your telemetry by passing `logger` or `onError`:

```tsx
<Boundary
  onError={(error, info) => {
    Sentry.captureException(error, { extra: { componentStack: info.componentStack } });
  }}
>
  …
</Boundary>
```

Or use `MonitorBoundary` from `@djangocfg/layouts` for automatic reporting to `@djangocfg/devtools`.

---

## Safety guarantees

- **Fallback can throw safely.** If the user's fallback render itself errors, the boundary degrades to a minimal static alert instead of looping forever.
- **`onError` / `onReset` can throw safely.** Caught and logged via `logger`. Won't crash the boundary.
- **Non-`Error` throws are normalized.** `throw 'oops'`, `throw { code: 500 }` and bare objects become real `Error` instances with stack traces (where possible).
- **No duplicate `onError` calls.** Internal tracking prevents firing twice for the same error instance.
- **Reset clears state before `onReset`.** Errors thrown inside `onReset` don't re-trigger the just-cleared boundary.

---

## Pairing with `<Suspense>`

Put `<Boundary>` **outside** `<Suspense>` — otherwise errors thrown by a suspended component bubble past it.

```tsx
<Boundary variant="card">
  <Suspense fallback={<Spinner />}>
    <DataPanel />
  </Suspense>
</Boundary>
```

---

## Edge cases & gotchas

| Issue | Cause | Solution |
|---|---|---|
| Boundary doesn't catch error | Error thrown in async code / event handler | Use `useBoundary().showBoundary(err)` |
| Boundary doesn't catch error (SSR) | `componentDidCatch` doesn't run on server | Errors are caught on client hydration. For SSR-only errors, use Next.js `error.tsx` |
| Infinite reset loop | `resetKeys` contains unstable values | Don't put new objects/arrays/random in `resetKeys` |
| Fallback renders briefly with stale data | React 18 concurrent rendering / `useDeferredValue` | Expected — the boundary unmounts children on error |
| `error.stack` is missing | Code threw a non-`Error` value | Boundary normalizes, but stack is reconstructed from current line. Prefer `throw new Error(...)` |
| Component stack only in dev | React strips it in prod by default | Use `onError`'s `info.componentStack` server-side via monitor |

---

## API

```ts
interface BoundaryProps {
  children: ReactNode;
  variant?: 'silent' | 'inline' | 'card' | 'fullscreen';  // default 'card'
  fallback?: ReactNode | ((props: BoundaryRenderProps) => ReactNode);
  FallbackComponent?: ComponentType<BoundaryRenderProps>;
  resetKeys?: ReadonlyArray<unknown>;
  onError?: (error: Error, info: ErrorInfo) => void;
  onReset?: (details: BoundaryResetDetails) => void;
  name?: string;           // dev log tag
  className?: string;      // fallback wrapper className
  logger?: BoundaryLogger; // override default console.error in dev
}

interface BoundaryRenderProps {
  error: Error;
  errorInfo: ErrorInfo | null;
  reset: () => void;
}

interface BoundaryResetDetails {
  reason: 'imperative' | 'keys';
  prevResetKeys?: ReadonlyArray<unknown>;
  nextResetKeys?: ReadonlyArray<unknown>;
}

function useBoundary(): {
  showBoundary: (error: unknown) => void;
  resetBoundary: () => void;
};
```

---

## Comparison with `react-error-boundary`

| Feature | `react-error-boundary` | `@djangocfg/ui-core` `Boundary` |
|---|---|---|
| `fallback` / `fallbackRender` / `FallbackComponent` | ✅ separate props | ✅ unified: `fallback` (node or fn) + `FallbackComponent` |
| `resetKeys` | ✅ | ✅ (shallow `Object.is` per index) |
| `onError` | ✅ | ✅ |
| `onReset` | ✅ | ✅ (with `reason` + prev/next keys) |
| `useErrorBoundary()` / `useBoundary()` | ✅ | ✅ |
| Built-in visual variants | ❌ | ✅ silent / inline / card / fullscreen |
| Safe fallback rendering | ❌ (can loop) | ✅ |
| `onError` / `onReset` thrown errors caught | ❌ | ✅ |
| Non-Error normalization | ❌ | ✅ |
| Accessible defaults (`role`, `aria-live`) | ❌ | ✅ |
| Backend telemetry integration | manual | `MonitorBoundary` wrapper |

---

## Related

- **`MonitorBoundary`** (`@djangocfg/layouts`) — wraps `Boundary` and reports to `@djangocfg/devtools` automatically.
- **Next.js `error.tsx`** — handles route-level errors. Use `Boundary` *inside* pages for finer granularity.
