/**
 * Framework-agnostic entry point. Zero React, zero Next.
 *
 * Import from here in a Vite/vanilla app, or anywhere you want the client
 * without pulling React into the graph.
 */

export { AnalyticsClient } from './client'
export { getAnalytics } from './global'
export type { AnalyticsAPI } from './global'
export type { AnalyticsEventPayload, AnalyticsOptions, AnalyticsTransport } from './types'

/**
 * The batched beacon transport. Also imported by @djangocfg/devtools — the
 * unload-delivery rules (sendBeacon's silent-failure trap, the shared keepalive
 * quota) are implemented ONCE, here, rather than re-derived per consumer.
 */
export { BeaconTransport } from './transport'
export type { BeaconOptions } from './transport'

export { djangocfg } from '../transports/djangocfg'
export type { DjangoCfgTransportOptions } from '../transports/djangocfg'
export { ga4 } from '../transports/ga4'
export type { Ga4TransportOptions } from '../transports/ga4'
