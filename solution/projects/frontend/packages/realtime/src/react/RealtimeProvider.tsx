'use client';

import { useAuth, useSession } from '@djangocfg/api/auth';
import { useEffect, useRef, useState } from 'react';

import { createRealtimeClient, realtimeUrl } from '../client';
import { RealtimeClientProvider } from './context';

import type { ReactNode } from 'react';
import type { RealtimeClient, ReportedIssue } from '../client';

export interface RealtimeConfig {
  /** Full socket URL. Default: `apiUrl` (or the page origin) with `path`, `ws:`/`wss:` by scheme. */
  url?: string;
  /** API origin the default URL is derived from. */
  apiUrl?: string;
  /** Default `/ws`. */
  path?: string;
  /** Default refetch for a topic whose history no longer reaches our offset. */
  onGap?: (topic: string) => void;
  /** A real realtime problem (see `RealtimeIssue`); `BaseApp` sends it to `@djangocfg/devtools`. */
  onIssue?: (issue: ReportedIssue) => void;
}

export interface RealtimeProviderProps extends RealtimeConfig {
  children: ReactNode;
}

function socketUrl(config: RealtimeConfig): string {
  if (config.url) return config.url;
  return realtimeUrl(config.apiUrl || globalThis.location.origin, config.path);
}

/**
 * One realtime client per app, wired to the session of `@djangocfg/api`. Opens
 * nothing by itself: the first `useTopic` connects. Mount it inside the auth
 * provider; on the server it renders its children with no client.
 *
 * Auth: the token from `useAuth().getToken()` goes as the first frame; a
 * session flip (login, logout) reconnects with the new identity; any other
 * session change (a refreshed token) retries a connection stopped by 4401.
 * Close 4419 refreshes the token through `useAuth().refreshToken()`.
 */
export function RealtimeProvider({ children, onGap, ...config }: RealtimeProviderProps) {
  const auth = useAuth();
  const session = useSession();
  const authRef = useRef(auth);
  const configRef = useRef(config);
  useEffect(() => {
    authRef.current = auth;
    configRef.current = config;
  });

  // No dispose on unmount: StrictMode would dispose the client it keeps. With no
  // subscribers left the client closes its socket by itself after the idle delay.
  const [client] = useState<RealtimeClient | null>(() =>
    typeof window === 'undefined'
      ? null
      : createRealtimeClient({
          url: () => socketUrl(configRef.current),
          onIssue: (issue) => {
            const sink = configRef.current.onIssue;
            if (sink) sink(issue);
            else console.warn('[realtime]', issue);
          },
          getToken: () => authRef.current.getToken(),
          // Payloads are checked against their typed topic's schema in development only.
          validateEvents: process.env.NODE_ENV !== 'production',
          refreshCredentials: async () => {
            const result = await authRef.current.refreshToken();
            return result.success;
          },
        }),
  );

  const status = useRef(session.status);
  useEffect(() => {
    if (client === null) return;
    if (status.current !== session.status) {
      status.current = session.status;
      client.authChanged();
    } else {
      client.resume();
    }
  }, [client, session]);

  // The server renders without a client, so the first client render must too, or every branch on
  // `useRealtimeClient()` fails hydration. Subscriptions start from effects, so nothing is lost.
  const [hydrated, setHydrated] = useState(false);
  useEffect(() => setHydrated(true), []);

  return (
    <RealtimeClientProvider client={hydrated ? client : null} onGap={onGap}>
      {children}
    </RealtimeClientProvider>
  );
}
