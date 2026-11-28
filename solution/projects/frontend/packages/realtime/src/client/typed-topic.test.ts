import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createMockServer } from '../testing';
import { createRealtimeClient } from './realtime-client';

import type { EventSchema, RealtimeTopic } from './typed-topic';

interface OrderEvent {
  status: string;
}

const orderSchema: EventSchema<OrderEvent> = {
  safeParse(data) {
    if (typeof data === 'object' && data !== null && 'status' in data && typeof data.status === 'string') {
      return { success: true, data: { status: data.status } };
    }
    return { success: false, error: new Error('status must be a string') };
  },
};

/** The shape the generated `ordersTopic({ orderId })` returns. */
function ordersTopic({ orderId }: { orderId: number }): RealtimeTopic<OrderEvent> {
  return { name: `orders:${orderId}`, pattern: 'orders:{order_id:int}', anonymous: false, schema: orderSchema };
}

function setup(validateEvents: boolean) {
  const server = createMockServer({ ping: 0 });
  const onInvalidEvent = vi.fn();
  const client = createRealtimeClient({
    url: server.url,
    WebSocket: server.WebSocket,
    random: () => 0,
    wake: () => () => {},
    validateEvents,
    onInvalidEvent,
  });
  return { server, client, onInvalidEvent };
}

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

describe('typed topics', () => {
  it('subscribes by the topic name and types the payload', async () => {
    const { server, client } = setup(true);
    const statuses: string[] = [];
    client.subscribe(ordersTopic({ orderId: 42 }), (event) => statuses.push(event.status));
    await vi.advanceTimersByTimeAsync(0);
    expect(server.subscribers('orders:42')).toBe(1);
    server.publish('orders:42', { status: 'paid' });
    await vi.advanceTimersByTimeAsync(0);
    expect(statuses).toEqual(['paid']);
  });

  it('reports and drops a payload that fails the schema while validating', async () => {
    const { server, client, onInvalidEvent } = setup(true);
    const onEvent = vi.fn();
    client.subscribe(ordersTopic({ orderId: 42 }), onEvent);
    await vi.advanceTimersByTimeAsync(0);
    server.publish('orders:42', { status: 7 });
    await vi.advanceTimersByTimeAsync(0);
    expect(onEvent).not.toHaveBeenCalled();
    expect(onInvalidEvent).toHaveBeenCalledWith('orders:42', expect.any(Error), { status: 7 });
  });

  it('reports a schema failure as an issue when no handler is given', async () => {
    const server = createMockServer({ ping: 0 });
    const onIssue = vi.fn();
    const client = createRealtimeClient({
      url: server.url,
      WebSocket: server.WebSocket,
      wake: () => () => {},
      validateEvents: true,
      onIssue,
    });
    client.subscribe(ordersTopic({ orderId: 42 }), () => {});
    await vi.advanceTimersByTimeAsync(0);
    server.publish('orders:42', { status: 7 });
    await vi.advanceTimersByTimeAsync(0);
    expect(onIssue).toHaveBeenCalledWith({
      kind: 'invalid_event',
      topic: 'orders:42',
      message: 'status must be a string',
      cid: 'c1',
    });
  });

  it('does not run the schema when validation is off', async () => {
    const { server, client } = setup(false);
    const spy = vi.spyOn(orderSchema, 'safeParse');
    const onEvent = vi.fn();
    client.subscribe(ordersTopic({ orderId: 42 }), onEvent);
    await vi.advanceTimersByTimeAsync(0);
    server.publish('orders:42', { status: 'paid' });
    await vi.advanceTimersByTimeAsync(0);
    expect(spy).not.toHaveBeenCalled();
    expect(onEvent).toHaveBeenCalledTimes(1);
    spy.mockRestore();
  });
});
