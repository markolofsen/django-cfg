/**
 * Google Analytics 4 transport.
 *
 * This is the old `packages/layouts/src/snippets/Analytics` layer, turned into a
 * transport. It kept its own route listener; now it is one destination among N,
 * fed by the single listener in core/client.ts. Two listeners would double-fire
 * with drifting taxonomies.
 *
 * `react-ga4` is loaded LAZILY, so a project that does not pass a GA4 tracking
 * id never pays for the library at all.
 *
 * Behavior change worth knowing about: the old layer hard-gated on `isProd`, so
 * it was completely silent in development. That gate is not reproduced here —
 * whether to track in dev is now the caller's decision (`debug` on the client),
 * not a hardcoded rule. GA4 still filters its own internal traffic server-side.
 */

import type { AnalyticsTransport } from '../core/types'

export interface Ga4TransportOptions {
  /** Measurement ID, e.g. `G-XXXXXXXXXX`. */
  trackingId: string
}

export function ga4(options: Ga4TransportOptions): AnalyticsTransport {
  const { trackingId } = options

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let ReactGA: any = null

  return {
    name: 'ga4',

    async init() {
      if (!trackingId) return
      const mod = await import('react-ga4')
      ReactGA = mod.default ?? mod
      ReactGA.initialize(trackingId)
    },

    pageview(event) {
      if (!ReactGA) return
      const search = (event.props?.search as string) || ''
      ReactGA.send({ hitType: 'pageview', page: `${event.pathname}${search}` })
    },

    event(event) {
      if (!ReactGA) return
      ReactGA.event(event.event_name, event.props ?? {})
    },

    identify(userId) {
      if (!ReactGA) return
      // Clearing must send an explicit null, not an omission — GA4 keeps the
      // previous user_id otherwise, and it would bleed into the next session.
      ReactGA.set({ user_id: userId })
    },
  }
}
