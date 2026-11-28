# @djangocfg/analytics

First-party product analytics for DjangoCFG. One client fans out pageviews and
custom events to django-cfg and optional GA4 transports.

## Product events

Mount `AnalyticsProvider` once (Layouts `BaseApp` does this automatically),
then use the typed React API:

```tsx
import { useAnalytics } from '@djangocfg/analytics'

const { event } = useAnalytics()
event('layouts.auth.step_viewed', { step: 'otp' })
event('billing.checkout_started', { plan: 'pro' })
```

For browser integration code outside React, use the optional facade installed
by the provider. It is the same client — not a second transport:

```ts
window.analytics?.event('billing.checkout_started', { plan: 'pro' })
```

Unknown product event names are accepted. Extend `AnalyticsEventMap` to make
your product's names and properties type-safe everywhere:

```ts
declare module '@djangocfg/analytics' {
  interface AnalyticsEventMap {
    'billing.checkout_started': { plan: 'pro' | 'team' }
  }
}
```

Use stable event names as your analytics contract. Django goals and funnels are
configured against those names; do not encode dynamic identifiers in names —
put bounded, non-sensitive dimensions in `props` instead.

## Identity and funnels

Browser journeys are scoped to a host. A property can aggregate hosts, but it
does not merge anonymous visitor identities across them. Server-confirmed auth
events use the request-derived identity for their originating host, so an auth
funnel on that host can join its UI and successful-login events safely.
