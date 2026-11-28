'use client';

import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect } from 'react';

import { setRealtimeCidProvider } from '@djangocfg/api';
import { devtools } from '@djangocfg/devtools';
import { RealtimeProvider, useRealtimeClient } from '@djangocfg/realtime/react';

import type { ReactNode } from 'react';
import type { ReportedIssue } from '@djangocfg/realtime';
import type { RealtimeConfig } from '@djangocfg/realtime/react';

import { bridgeQueryCache, topicsOfQuery } from './queryRealtime';
import { realtimeIssueEvent } from './realtimeIssueEvent';

interface RealtimeMountProps {
  config: RealtimeConfig;
  apiUrl: string | undefined;
  children: ReactNode;
}

/**
 * Points `@djangocfg/api`'s `X-Realtime-Cid` header at this tab's socket, so a
 * write's own publication is not echoed back to it. Cleared on unmount.
 */
function RealtimeCidBridge() {
  const client = useRealtimeClient();
  useEffect(() => {
    if (client === null) return;
    setRealtimeCidProvider(() => client.getCid());
    return () => setRealtimeCidProvider(null);
  }, [client]);
  return null;
}

/** Keeps the topics of the mounted, tagged queries subscribed; see `bridgeQueryCache`. */
function RealtimeQueryBridge() {
  const client = useRealtimeClient();
  const queryClient = useQueryClient();
  useEffect(() => (client === null ? undefined : bridgeQueryCache(queryClient, client)), [client, queryClient]);
  return null;
}

/** Realtime problems go to the same monitor as every other frontend error. Never throws. */
function captureIssue(issue: ReportedIssue): void {
  try {
    devtools.capture(realtimeIssueEvent(issue, typeof window !== 'undefined' ? window.location.href : undefined));
  } catch {
    // Monitoring must not break the socket.
  }
}

/**
 * `RealtimeProvider` with the app's defaults. A generated query whose operation is `invalidated_by` a topic carries
 * it in `meta.realtimeTopics`; while such a query is mounted its topics stay subscribed, and a message or a gap
 * invalidates it, so the REST API stays the source of truth and a page needs no code (`RealtimeQueryBridge`). Unless
 * the app passes `onGap`, a gap on a `useTopic` subscription invalidates the queries tagged with that topic too.
 * Issues are captured by `@djangocfg/devtools` (an app's own `onIssue` runs as well). Sits inside the app's
 * QueryClient and `AuthProvider`.
 */
export function RealtimeMount({ config, apiUrl, children }: RealtimeMountProps) {
  const queryClient = useQueryClient();
  const invalidateTopic = useCallback(
    (topic: string) => {
      void queryClient.invalidateQueries({ predicate: (query) => topicsOfQuery(query).includes(topic) });
    },
    [queryClient],
  );
  const appOnIssue = config.onIssue;
  const onIssue = useCallback(
    (issue: ReportedIssue) => {
      captureIssue(issue);
      appOnIssue?.(issue);
    },
    [appOnIssue],
  );
  return (
    <RealtimeProvider {...config} apiUrl={apiUrl} onGap={config.onGap ?? invalidateTopic} onIssue={onIssue}>
      <RealtimeCidBridge />
      <RealtimeQueryBridge />
      {children}
    </RealtimeProvider>
  );
}
