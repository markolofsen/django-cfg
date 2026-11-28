import { describe, expect, it } from 'vitest';

import { isTerminalClose, isTopicName } from './frames';
import { parseFrame } from './parse-frame';

describe('parseFrame', () => {
  it('accepts every server frame of protocol v1 and drops unknown fields', () => {
    const frames = [
      { op: 'hello', v: 1, user: 7, ping: 25, cid: 'c1', extra: true },
      { op: 'hello', v: 1, user: null, ping: 25, cid: 'c1' },
      { op: 'sub_ok', id: 1, topic: 'orders:42', offset: '5-0', recovered: false },
      { op: 'sub_ok', id: 1, topic: 'orders:42', offset: '5-0' },
      { op: 'sub_err', id: 2, topic: 'orders:42', code: 'forbidden' },
      { op: 'msg', topic: 'orders:42', offset: '6-0', data: { status: 'paid' } },
      { op: 'msg', topic: 'orders:42', offset: '7-0', data: null, origin_cid: 'c2' },
      { op: 'sub_err', id: 3, topic: 'orders:42', code: 'timeout' },
      { op: 'pong' },
      { op: 'error', code: 'bad_json', detail: 'x' },
    ];
    const parsed = frames.map((f) => parseFrame(JSON.stringify(f)));
    expect(parsed.every((p) => p.ok)).toBe(true);
    expect(parsed[0]).toEqual({ ok: true, frame: { op: 'hello', v: 1, user: 7, ping: 25, cid: 'c1' } });
    expect(parsed[3]).toEqual({ ok: true, frame: { op: 'sub_ok', id: 1, topic: 'orders:42', offset: '5-0' } });
  });

  it('refuses an unknown op, a bad shape and non-JSON without throwing', () => {
    const bad = [
      'not json',
      '[]',
      JSON.stringify({ op: 'presence' }),
      JSON.stringify({ op: 'ping' }),
      JSON.stringify({ op: 'hello', v: 1, user: 1, ping: 25, boot: 'b' }),
      JSON.stringify({ op: 'msg', topic: 'a', offset: 1, data: {} }),
      JSON.stringify({ op: 'msg', topic: 'a', offset: '1' }),
      JSON.stringify({ op: 'sub_err', id: 1, topic: 'a', code: 'nope' }),
      JSON.stringify({ op: 'sub_ok', id: 1, topic: 'a', offset: '1', recovered: 'yes' }),
      JSON.stringify({ op: 'hello', v: 1, user: {}, ping: 25, cid: 'c' }),
    ];
    for (const text of bad) expect(parseFrame(text).ok).toBe(false);
  });
});

describe('topics and close codes', () => {
  it('matches the server topic grammar', () => {
    expect(['orders:42', 'demo.ping', 'demo.user:7', 'a-b_c:X.y-1:z'].every(isTopicName)).toBe(true);
    expect(['', 'Orders', 'orders:', 'orders 42', ':x', 'a::b'].some(isTopicName)).toBe(false);
  });

  it('stops only on 4401 and 4403', () => {
    expect([4401, 4403].every(isTerminalClose)).toBe(true);
    expect([1000, 1006, 1011, 1012, 1013, 4408, 4419, 4429, 4500].some(isTerminalClose)).toBe(false);
  });
});
