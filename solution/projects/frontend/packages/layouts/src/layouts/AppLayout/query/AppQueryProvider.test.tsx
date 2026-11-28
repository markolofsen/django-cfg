// @vitest-environment jsdom
import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query';
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { describe, expect, it } from 'vitest';

import { AppQueryProvider, QUERY_MAX_RETRIES, createAppQueryClient, shouldRetryQuery } from './AppQueryProvider';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

function clientUnder(tree: (probe: React.ReactNode) => React.ReactNode): QueryClient {
  let seen: QueryClient | null = null;
  function Probe() {
    seen = useQueryClient();
    return null;
  }
  const root = createRoot(document.createElement('div'));
  act(() => root.render(<>{tree(<Probe />)}</>));
  act(() => root.unmount());
  if (seen === null) throw new Error('no QueryClient reached the probe');
  return seen;
}

describe('shouldRetryQuery', () => {
  it('never retries a 4xx, retries a 5xx and a network failure up to the limit', () => {
    expect(shouldRetryQuery(0, { statusCode: 404 })).toBe(false);
    expect(shouldRetryQuery(0, { status: 401 })).toBe(false);
    expect(shouldRetryQuery(0, { statusCode: 502 })).toBe(true);
    expect(shouldRetryQuery(0, Object.assign(new Error('offline'), { name: 'NetworkError' }))).toBe(true);
    expect(shouldRetryQuery(0, new TypeError('Failed to fetch'))).toBe(true);
    expect(shouldRetryQuery(QUERY_MAX_RETRIES, { statusCode: 503 })).toBe(false);
    expect(shouldRetryQuery(0, new Error('response failed validation'))).toBe(false);
  });

  it('is the default of the client BaseApp creates, with mutations not retried', () => {
    const defaults = createAppQueryClient().getDefaultOptions();
    expect(defaults.queries?.retry).toBe(shouldRetryQuery);
    expect(defaults.queries?.throwOnError).toBe(false);
    expect(defaults.mutations?.retry).toBe(false);
  });
});

describe('AppQueryProvider', () => {
  it('reuses a QueryClient provided above it instead of nesting a second cache', () => {
    const outer = new QueryClient();
    const seen = clientUnder((probe) => (
      <QueryClientProvider client={outer}>
        <AppQueryProvider>{probe}</AppQueryProvider>
      </QueryClientProvider>
    ));
    expect(seen).toBe(outer);
  });

  it("uses the app's own client as it is", () => {
    const own = new QueryClient();
    const seen = clientUnder((probe) => <AppQueryProvider queryClient={own}>{probe}</AppQueryProvider>);
    expect(seen).toBe(own);
    expect(seen.getDefaultOptions().queries?.retry).toBeUndefined();
  });

  it("creates one with django-cfg's defaults when there is none", () => {
    const seen = clientUnder((probe) => <AppQueryProvider>{probe}</AppQueryProvider>);
    expect(seen.getDefaultOptions().queries?.retry).toBe(shouldRetryQuery);
  });
});
