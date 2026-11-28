import { describe, expect, it } from 'vitest';

import { decodeStored } from './storage-decode';

const wrap = (value: unknown, ttl: number, createdAt = Date.now()) =>
  JSON.stringify({ _meta: { createdAt, ttl }, _value: value });

describe('decodeStored', () => {
  it('reads a value of the expected type', () => {
    expect(decodeStored('42', 0)).toEqual({ ok: true, value: 42 });
    expect(decodeStored('true', false)).toEqual({ ok: true, value: true });
    expect(decodeStored('["a"]', [] as string[])).toEqual({ ok: true, value: ['a'] });
  });

  it('keeps a bare string (strings are stored without quotes)', () => {
    expect(decodeStored('ru-RU', '')).toEqual({ ok: true, value: 'ru-RU' });
  });

  it('refuses garbage instead of casting it into the wrong type', () => {
    expect(decodeStored('ru-RU', { a: 1 })).toEqual({ ok: false, reason: 'invalid' });
    expect(decodeStored('{broken', 5)).toEqual({ ok: false, reason: 'invalid' });
    expect(decodeStored('"text"', 5)).toEqual({ ok: false, reason: 'invalid' });
    expect(decodeStored('{"a":1}', [] as number[])).toEqual({ ok: false, reason: 'invalid' });
    expect(decodeStored('[1]', { a: 1 })).toEqual({ ok: false, reason: 'invalid' });
  });

  it('absent is not an error', () => {
    expect(decodeStored(null, 'x')).toEqual({ ok: false, reason: 'absent' });
  });

  it('fills a field added in a later release from the initial value', () => {
    expect(decodeStored('{"a":2}', { a: 1, b: 'new' })).toEqual({ ok: true, value: { a: 2, b: 'new' } });
  });

  it('rejects an object whose field changed type', () => {
    expect(decodeStored('{"a":"two"}', { a: 1 })).toEqual({ ok: false, reason: 'invalid' });
  });

  it('honours a TTL wrapper and reports expiry', () => {
    expect(decodeStored(wrap('v', 1000), '')).toEqual({ ok: true, value: 'v' });
    expect(decodeStored(wrap('v', 1000, Date.now() - 5000), '')).toEqual({ ok: false, reason: 'expired' });
  });

  it('lets a validator decide, and survives one that throws', () => {
    const isMode = (v: unknown): v is 'a' | 'b' => v === 'a' || v === 'b';
    expect(decodeStored('"b"', 'a' as 'a' | 'b', isMode)).toEqual({ ok: true, value: 'b' });
    expect(decodeStored('"z"', 'a' as 'a' | 'b', isMode)).toEqual({ ok: false, reason: 'invalid' });
    const boom = (): boolean => {
      throw new Error('x');
    };
    expect(decodeStored('1', 0, boom as never)).toEqual({ ok: false, reason: 'invalid' });
  });

  it('accepts anything when the caller declared no shape', () => {
    expect(decodeStored('{"a":1}', null)).toEqual({ ok: true, value: { a: 1 } });
  });
});
