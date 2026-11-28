/**
 * First-party transport: POST to django-cfg's /cfg/analytics/<path>/.
 *
 * The delivery rules (unload flush, sendBeacon's silent-failure trap, the shared
 * keepalive quota) live in ../core/transport.ts — ONE implementation, shared with
 * @djangocfg/devtools. Do not re-implement them here.
 */

import { BeaconTransport } from '../core/transport'
import type { AnalyticsEventPayload, AnalyticsTransport } from '../core/types'

export interface DjangoCfgTransportOptions {
  /**
   * Where to POST. Defaults to `${NEXT_PUBLIC_API_URL}/cfg/analytics/collect/`,
   * so it stays relative same-origin when the API shares the frontend's origin
   * (empty base — no CORS, no preflight, dodges ad blockers) and becomes
   * absolute on a split-domain deploy where the API lives elsewhere.
   *
   * Configurable because filter lists (EasyPrivacy et al.) match on PATH, not
   * domain: a fixed path shipped in an open-source package gets blocked once,
   * for everyone.
   */
  ingestPath?: string

  /** Which registered AnalyticsSite these events belong to. */
  site?: string

  /**
   * The signed-in user's access token, read at send time.
   *
   * The beacon cannot set an Authorization header, so the token travels in the body.
   * The server verifies it like a Bearer token, keeps only the user id, and treats a
   * bad or expired one as an anonymous hit. Return null when signed out.
   */
  getAuthToken?: () => string | null | undefined

  /** Max events per request. The server caps at 25. */
  batchSize?: number
}

export function djangocfg(options: DjangoCfgTransportOptions = {}): AnalyticsTransport {
  const apiBase = (process.env.NEXT_PUBLIC_API_URL ?? '').replace(/\/+$/, '')
  const ingestPath = options.ingestPath ?? `${apiBase}/cfg/analytics/collect/`
  const site = options.site ?? (typeof window !== 'undefined' ? window.location.hostname : '')

  let userId: string | null = null

  const beacon = new BeaconTransport({
    url: ingestPath,
    batchSize: Math.min(options.batchSize ?? 25, 25),
    // credentials:'include' is what lets the server resolve request.user and
    // attribute the event to a signed-in account — the differentiator.
    credentials: 'include',
    serialize: (events) => {
      let auth = ''
      try {
        auth = options.getAuthToken?.() || ''
      } catch {
        // Telemetry must never throw into the page.
      }
      return JSON.stringify(auth ? { site, events, auth } : { site, events })
    },
  })

  const enqueue = (event: AnalyticsEventPayload) => {
    beacon.push({
      ...event,
      props: { ...event.props, ...(userId ? { user_id: userId } : {}) },
    })
  }

  return {
    name: 'djangocfg',
    pageview: (event) => enqueue({ ...event, event_name: 'pageview' }),
    event: (event) => enqueue(event),
    identify: (id) => {
      userId = id
    },
    flush: (final) => beacon.flush(final),
  }
}
