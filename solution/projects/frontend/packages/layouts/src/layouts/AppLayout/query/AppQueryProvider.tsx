'use client';

import { QueryClient, QueryClientContext, QueryClientProvider } from '@tanstack/react-query';
import { Suspense, lazy, useContext, useMemo, useState } from 'react';

import type { ComponentType, ReactNode } from 'react';

/** Retries after a failure: none on a 4xx or a non-network error, up to this many on a network error or a 5xx. */
export const QUERY_MAX_RETRIES = 2;
/** How long a fetched query counts as fresh before a mount or a focus refetches it. */
export const QUERY_STALE_TIME_MS = 30_000;

function statusOf(error: unknown): number | null {
  if (typeof error !== 'object' || error === null) return null;
  const { statusCode, status } = error as { statusCode?: unknown; status?: unknown };
  if (typeof statusCode === 'number' && statusCode > 0) return statusCode;
  if (typeof status === 'number' && status > 0) return status;
  return null;
}

/**
 * Structural, not `instanceof`: a 5xx or a failed connection is worth another try; a 4xx, a response that failed
 * validation or a configuration error will fail the same way again.
 */
export function shouldRetryQuery(failureCount: number, error: unknown): boolean {
  if (failureCount >= QUERY_MAX_RETRIES) return false;
  const status = statusOf(error);
  if (status !== null) return status >= 500;
  const name = error instanceof Error ? error.name : '';
  return name === 'NetworkError' || name === 'TypeError';
}

/** A new QueryClient with django-cfg's defaults. One per mounted app: never at module scope (SSR). */
export function createAppQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: shouldRetryQuery,
        throwOnError: false,
        staleTime: QUERY_STALE_TIME_MS,
        refetchOnWindowFocus: true,
      },
      mutations: { retry: false },
    },
  });
}

/** `() => import('@tanstack/react-query-devtools')`: the app's own import, so the package is the app's choice. */
export type QueryDevtoolsLoader = () => Promise<{ ReactQueryDevtools: ComponentType<{ initialIsOpen?: boolean }> }>;

export interface AppQueryProviderProps {
  /** The app's own client. It wins and its defaults are used as they are. */
  queryClient?: QueryClient;
  /** React Query Devtools, rendered in development only and loaded lazily. */
  queryDevtools?: QueryDevtoolsLoader;
  children: ReactNode;
}

function QueryDevtools({ load }: { load: QueryDevtoolsLoader }) {
  const Devtools = useMemo(() => lazy(() => load().then((m) => ({ default: m.ReactQueryDevtools }))), [load]);
  return (
    <Suspense fallback={null}>
      <Devtools initialIsOpen={false} />
    </Suspense>
  );
}

/**
 * The app's QueryClient. `queryClient` wins; else a QueryClient already provided above is reused, so a page never
 * holds two caches; else one is created with `createAppQueryClient` for the life of this mount.
 */
export function AppQueryProvider({ queryClient, queryDevtools, children }: AppQueryProviderProps) {
  const outer = useContext(QueryClientContext);
  // Created once per mount even when unused: a QueryClient that is never provided holds nothing and starts nothing.
  const [own] = useState(createAppQueryClient);
  const devtools =
    queryDevtools && process.env.NODE_ENV !== 'production' ? <QueryDevtools load={queryDevtools} /> : null;

  const client = queryClient ?? (outer ? null : own);
  if (client === null) {
    return (
      <>
        {children}
        {devtools}
      </>
    );
  }
  return (
    <QueryClientProvider client={client}>
      {children}
      {devtools}
    </QueryClientProvider>
  );
}
