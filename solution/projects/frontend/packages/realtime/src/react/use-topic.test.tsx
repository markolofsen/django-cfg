// @vitest-environment jsdom
import { act, render } from '@testing-library/react';
import { StrictMode } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createRealtimeClient } from '../client';
import { createMockServer } from '../testing';
import { RealtimeClientProvider } from './context';
import { useTopic } from './use-topic';

function Feed({ topic, onEvent }: { topic: string; onEvent: (data: unknown) => void }) {
  const state = useTopic(topic, onEvent);
  return <output>{state?.status ?? 'none'}</output>;
}

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

describe('useTopic', () => {
  it('subscribes once under StrictMode, follows the latest handler and releases on unmount', async () => {
    const server = createMockServer({ ping: 0 });
    const client = createRealtimeClient({
      url: server.url,
      WebSocket: server.WebSocket,
      random: () => 0,
      wake: () => () => {},
    });
    const first = vi.fn();
    const second = vi.fn();
    const view = render(
      <StrictMode>
        <RealtimeClientProvider client={client}>
          <Feed topic="demo.ping" onEvent={first} />
        </RealtimeClientProvider>
      </StrictMode>,
    );
    await act(() => vi.advanceTimersByTimeAsync(10_000));
    const ops = () => server.received.map((r) => r.frame.op);
    expect(ops().filter((op) => op === 'sub')).toHaveLength(1);
    expect(ops()).not.toContain('unsub');
    expect(view.container.textContent).toBe('live');

    view.rerender(
      <StrictMode>
        <RealtimeClientProvider client={client}>
          <Feed topic="demo.ping" onEvent={second} />
        </RealtimeClientProvider>
      </StrictMode>,
    );
    server.publish('demo.ping', { n: 1 });
    await act(() => vi.advanceTimersByTimeAsync(0));
    expect(first).not.toHaveBeenCalled();
    expect(second).toHaveBeenCalledWith({ n: 1 }, expect.anything());

    view.unmount();
    await act(() => vi.advanceTimersByTimeAsync(1_500));
    expect(ops().filter((op) => op === 'unsub')).toHaveLength(1);
    await act(() => vi.advanceTimersByTimeAsync(30_000));
    expect(server.connections).toBe(0);
  });
});
