'use client';

import { createContext, useContext, useEffect, useMemo, useRef } from 'react';

import type { ReactNode } from 'react';
import type { RealtimeClient } from '../client';

interface RealtimeContextValue {
  client: RealtimeClient;
  /** The app-wide gap handler; a `useTopic` option overrides it. */
  gap(topic: string): void;
}

const RealtimeContext = createContext<RealtimeContextValue | null>(null);

export interface RealtimeClientProviderProps {
  /** `null` renders the children with no realtime (SSR, or switched off). */
  client: RealtimeClient | null;
  /** Default for every topic without its own `onGap`: refetch what the topic feeds. */
  onGap?: (topic: string) => void;
  children: ReactNode;
}

/**
 * Puts an existing client in context. `RealtimeProvider` creates one from the
 * app's auth; tests and stories pass a client wired to the mock server.
 */
export function RealtimeClientProvider({ client, onGap, children }: RealtimeClientProviderProps) {
  const onGapRef = useRef(onGap);
  useEffect(() => {
    onGapRef.current = onGap;
  }, [onGap]);

  // Stable while the client is: a new `onGap` each render must not resubscribe every topic.
  const value = useMemo<RealtimeContextValue | null>(
    () => (client === null ? null : { client, gap: (topic) => onGapRef.current?.(topic) }),
    [client],
  );
  return <RealtimeContext.Provider value={value}>{children}</RealtimeContext.Provider>;
}

export function useRealtimeContext(): RealtimeContextValue | null {
  return useContext(RealtimeContext);
}

/** The app's client, or `null` outside a provider and during SSR. */
export function useRealtimeClient(): RealtimeClient | null {
  return useContext(RealtimeContext)?.client ?? null;
}
