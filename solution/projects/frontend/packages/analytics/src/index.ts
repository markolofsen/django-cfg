/**
 * @djangocfg/analytics
 *
 * One route listener, N transports.
 *
 * @example
 * ```tsx
 * <AnalyticsProvider
 *   transports={[djangocfg({ site: 'example.com' }), ga4({ trackingId })]}
 *   userId={user?.id}
 * >
 *   <PageviewTracker route="/[locale]/blog/[slug]" locale={locale} />
 *   {children}
 * </AnalyticsProvider>
 * ```
 */

export { AnalyticsClient } from './core/client'
export { getAnalytics } from './core/global'
export type { AnalyticsAPI } from './core/global'
export type {
  AnalyticsEventPayload,
  AnalyticsOptions,
  AnalyticsTransport,
} from './core/types'

export { djangocfg } from './transports/djangocfg'
export type { DjangoCfgTransportOptions } from './transports/djangocfg'
export { ga4 } from './transports/ga4'
export type { Ga4TransportOptions } from './transports/ga4'

export { AnalyticsProvider, useAnalytics, useAnalyticsClient } from './react/context'
export type { AnalyticsProviderProps } from './react/context'

export { PageviewTracker } from './next/PageviewTracker'
export type { PageviewTrackerProps } from './next/PageviewTracker'

export { AnalyticsCategory, AnalyticsEvent } from './events'
export type {
  AnalyticsCategoryType,
  AnalyticsEventMap,
  AnalyticsEventName,
  AnalyticsEventProps,
  AnalyticsEventProperties,
  AnalyticsEventType,
  AnalyticsPropertyValue,
} from './events'
