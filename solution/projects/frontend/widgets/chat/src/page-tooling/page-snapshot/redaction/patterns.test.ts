import { describe, expect, it } from 'vitest';

import { redactPatterns } from './patterns';

describe('redactPatterns', () => {
  it('redacts a JWT', () => {
    // Deliberately invalid, in-memory test token; no signing key or real claims.
    const base64url = (text: string) =>
      btoa(text).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    const jwt = [
      base64url(JSON.stringify({ alg: 'HS256' })),
      base64url(JSON.stringify({ sub: 'fixture' })),
      base64url('not-a-valid-signature'),
    ].join('.');
    const { value, matched } = redactPatterns(`token is ${jwt} ok`);
    expect(matched).toContain('jwt');
    expect(value).not.toContain('eyJhbGci');
    expect(value).toContain('‹redacted:jwt›');
  });

  it('redacts a bearer token', () => {
    const { value, matched } = redactPatterns(
      'Authorization: Bearer abcdef1234567890ABCDEF',
    );
    expect(matched).toContain('bearer-token');
    expect(value).not.toContain('abcdef1234567890');
  });

  it('redacts API-key shapes', () => {
    const { matched } = redactPatterns('key sk-abcdefghijklmnop1234 end');
    expect(matched).toContain('api-key');
  });

  it('redacts an email address', () => {
    const { value, matched } = redactPatterns('mail me at jane@acme.com now');
    expect(matched).toContain('email');
    expect(value).not.toContain('jane@acme.com');
  });

  it('redacts a Luhn-valid card number', () => {
    const { value, matched } = redactPatterns('card 4242424242424242 charged');
    expect(matched).toContain('credit-card');
    expect(value).not.toContain('4242424242424242');
  });

  it('does NOT redact a Luhn-invalid long number (order id)', () => {
    // 16 digits but not a valid card — must survive (false-positive guard).
    const orderId = '1234567890123456';
    const { value, matched } = redactPatterns(`order ${orderId} shipped`);
    expect(matched).not.toContain('credit-card');
    expect(value).toContain(orderId);
  });

  it('redacts a phone number with separators or +', () => {
    expect(redactPatterns('call +1 (415) 555-2671 today').matched).toContain(
      'phone',
    );
    expect(redactPatterns('ph: 415-555-2671').matched).toContain('phone');
  });

  it('leaves clean text untouched', () => {
    const { value, matched } = redactPatterns('just a normal sentence');
    expect(matched).toEqual([]);
    expect(value).toBe('just a normal sentence');
  });
});
