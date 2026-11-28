# @djangocfg/devtools

Frontend devtools for django-cfg apps. One package, one event stream:

- **Capture** — `window.onerror`, unhandled rejections, `console.warn/error`,
  zod validation events from `@djangocfg/api` clients.
- **Ingest** — errors/warnings are batched to `POST /cfg/monitor/ingest/`
  (django-cfg's `django_monitor` extension) with dedupe, keepalive flush on
  unload, and a circuit breaker.
- **Debug panel** — floating button (auto in dev, `?debug=1` in prod, ⌘D)
  with a filterable log feed and app-defined custom tabs.

Replaces the retired `@djangocfg/monitor` + `@djangocfg/debuger` pair.

## Usage

```tsx
// Root layout — that's the whole setup
import { Devtools } from '@djangocfg/devtools'

<Devtools project="my-app" environment={process.env.NODE_ENV} />
```

```ts
// Anywhere in client code
import { devtools } from '@djangocfg/devtools'

devtools.error('Payment widget crashed', { orderId })   // panel + backend
const log = devtools.log('CheckoutForm')                // panel only
log.info('step changed', { step })
```

```ts
// Server (route handlers / RSC)
import { serverDevtools } from '@djangocfg/devtools/server'

serverDevtools.configure({ project: 'my-app', baseUrl: process.env.API_URL })
await serverDevtools.captureError(err, { url: req.url })
```

In the browser console: `window.devtools.status()`, `window.devtools.error('test')`.

## Is it reaching the backend?

Ingest needs the API origin: `<Devtools baseUrl>`, or in `BaseApp` `auth.apiUrl` /
`apiUrl` (for `auth={false}`), or `NEXT_PUBLIC_API_URL` baked in at build time.
With none, devtools warns once in the console and drops events.

- `devtools.status()` returns `{ ingest, baseUrl, queued, sent, failed, lastError, lastSentAt, circuitOpen }`.
- `await devtools.ping()` sends one info event (`devtools ping`) and resolves with `status()`.
- Server: `python manage.py monitor_tail --frontend`.
