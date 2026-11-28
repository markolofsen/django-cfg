/**
 * Imperative access to the one AnalyticsClient mounted by AnalyticsProvider.
 *
 * `window.analytics` is deliberately a thin optional facade, analogous to
 * `window.dialog` but not a second event pipeline. React code uses
 * `useAnalytics`; integration code without a React tree can use
 * `getAnalytics()?.event(...)`.
 */

import type { AnalyticsEventName, AnalyticsEventProps } from '../events'
import type { AnalyticsClient } from './client'

export interface AnalyticsAPI {
  event<Name extends AnalyticsEventName>(
    name: Name,
    props?: AnalyticsEventProps<Name>,
  ): void
  flush(): void
}

let activeApi: AnalyticsAPI | null = null

export function getAnalytics(): AnalyticsAPI | null {
  return activeApi
}

export function installAnalytics(client: AnalyticsClient): () => void {
  const api: AnalyticsAPI = {
    event: (name, props) => client.trackEvent(name, props),
    flush: () => client.flush(),
  }
  activeApi = api

  if (typeof window !== 'undefined') {
    window.analytics = api
  }

  return () => {
    if (activeApi !== api) return
    activeApi = null
    if (typeof window !== 'undefined' && window.analytics === api) {
      delete window.analytics
    }
  }
}

declare global {
  interface Window {
    /** Installed only while an AnalyticsProvider is mounted. */
    analytics?: AnalyticsAPI
  }
}
