'use client'

/**
 * React bindings. Router-agnostic: the provider owns the client, and a router
 * adapter (see ../next) feeds it location changes.
 */

import { createContext, useContext, useEffect, useMemo, useRef, type ReactNode } from 'react'

import { AnalyticsClient } from '../core/client'
import { installAnalytics } from '../core/global'
import type { AnalyticsOptions } from '../core/types'
import type { AnalyticsEventName, AnalyticsEventProps } from '../events'

const AnalyticsContext = createContext<AnalyticsClient | null>(null)

export interface AnalyticsProviderProps extends AnalyticsOptions {
  children: ReactNode

  /**
   * The signed-in user's id, or null/undefined when anonymous.
   *
   * MUST be an opaque id — never an email. And it MUST go back to null on
   * logout: a stale user_id attached to the next anonymous session is a real
   * privacy leak, not a cosmetic bug.
   */
  userId?: string | null
}

export function AnalyticsProvider({
  children,
  transports,
  debug,
  userId,
}: AnalyticsProviderProps) {
  // The client must survive React 19 StrictMode's dev remount, or its pageview
  // dedup key would reset and every pageview would fire twice.
  const clientRef = useRef<AnalyticsClient | null>(null)
  if (clientRef.current === null) {
    clientRef.current = new AnalyticsClient({ transports, debug })
  }
  const client = clientRef.current

  useEffect(() => {
    void client.init()
    const uninstall = installAnalytics(client)
    return () => {
      uninstall()
      client.destroy()
    }
  }, [client])

  useEffect(() => {
    // Inside an effect, never during render: reading auth state during render
    // produces a server/client hydration mismatch.
    client.identify(userId ?? null)
  }, [client, userId])

  return <AnalyticsContext.Provider value={client}>{children}</AnalyticsContext.Provider>
}

/**
 * Track custom events from a component.
 *
 * Returns a stable object, so it is safe in a dependency array.
 */
export function useAnalytics() {
  const client = useContext(AnalyticsContext)

  return useMemo(
    () => ({
      event: <Name extends AnalyticsEventName>(name: Name, props?: AnalyticsEventProps<Name>) =>
        client?.trackEvent(name, props),
      identify: (userId: string | null) => client?.identify(userId),
      flush: () => client?.flush(false),
      /** False when no AnalyticsProvider is mounted above this component. */
      isEnabled: client !== null,
    }),
    [client],
  )
}

/** Internal: the router adapters need the raw client. */
export function useAnalyticsClient(): AnalyticsClient | null {
  return useContext(AnalyticsContext)
}
