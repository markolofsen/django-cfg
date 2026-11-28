import { describe, expect, it } from 'vitest';

import { readOAuthCallback, stripOAuthCallbackParams } from './callbackParams';

const isProvider = (value: string): value is 'github' | 'google' => value === 'github' || value === 'google';
const read = (query: string) => readOAuthCallback(new URLSearchParams(query), isProvider);

describe('readOAuthCallback', () => {
  it('ignores a page that is not a callback', () => {
    expect(read('')).toEqual({ kind: 'none' });
    expect(read('code=abc&state=xyz')).toEqual({ kind: 'none' });
  });

  it('asks for the exchange when provider, code and state are present', () => {
    expect(read('provider=google&code=c1&state=s1&scope=openid&authuser=0&prompt=none')).toEqual({
      kind: 'exchange',
      provider: 'google',
      code: 'c1',
      state: 's1',
    });
  });

  it('treats Cancel (access_denied, no code) as a cancellation', () => {
    expect(read('provider=google&error=access_denied&state=s1')).toEqual({
      kind: 'failure',
      provider: 'google',
      code: 'cancelled',
      description: 'access_denied',
    });
  });

  it('carries the description of another provider error without naming a cause', () => {
    expect(read('provider=github&error=server_error&error_description=Oops')).toEqual({
      kind: 'failure',
      provider: 'github',
      code: undefined,
      description: 'Oops',
    });
  });

  it('prefers the provider error over a code', () => {
    expect(read('provider=google&error=access_denied&code=c1&state=s1').kind).toBe('failure');
  });

  it('rejects an unknown provider', () => {
    expect(read('provider=myspace&code=c1&state=s1')).toMatchObject({
      kind: 'failure',
      provider: 'myspace',
      code: 'unknown_provider',
    });
  });

  it('rejects a callback without code or state as an invalid state', () => {
    expect(read('provider=google&code=c1')).toMatchObject({ kind: 'failure', code: 'invalid_state' });
    expect(read('provider=google&state=s1')).toMatchObject({ kind: 'failure', code: 'invalid_state' });
    expect(read('provider=google')).toMatchObject({ kind: 'failure', code: 'invalid_state' });
  });
});

describe('stripOAuthCallbackParams', () => {
  it('removes every callback parameter and keeps the rest', () => {
    const href =
      'https://app.example.com/auth?provider=google&code=c1&state=s1&scope=openid+email&authuser=0&prompt=consent&hd=x.com&lang=de#top';
    expect(stripOAuthCallbackParams(href)).toBe('/auth?lang=de#top');
  });

  it('removes error parameters', () => {
    expect(
      stripOAuthCallbackParams('https://a.example/auth?provider=google&error=access_denied&error_description=x'),
    ).toBe('/auth');
  });

  it('leaves a clean URL alone', () => {
    expect(stripOAuthCallbackParams('https://a.example/auth#x/y?z=1')).toBe('/auth#x/y?z=1');
  });
});
