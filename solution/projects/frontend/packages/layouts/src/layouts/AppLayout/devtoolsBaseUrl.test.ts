import { describe, expect, it } from 'vitest';

import { resolveDevtoolsBaseUrl } from './devtoolsBaseUrl';

describe('resolveDevtoolsBaseUrl', () => {
  it('takes auth.apiUrl when auth is configured', () => {
    expect(resolveDevtoolsBaseUrl({ auth: { apiUrl: 'https://api.a.com' } })).toBe('https://api.a.com');
  });

  it('takes the apiUrl prop for auth={false} apps', () => {
    expect(resolveDevtoolsBaseUrl({ auth: false, apiUrl: 'https://api.b.com' })).toBe('https://api.b.com');
  });

  it('an explicit devtools.baseUrl wins, then apiUrl, then auth.apiUrl', () => {
    const all = { auth: { apiUrl: 'https://auth' }, apiUrl: 'https://prop', devtools: { baseUrl: 'https://dt' } };
    expect(resolveDevtoolsBaseUrl(all)).toBe('https://dt');
    expect(resolveDevtoolsBaseUrl({ ...all, devtools: {} })).toBe('https://prop');
    expect(resolveDevtoolsBaseUrl({ auth: all.auth })).toBe('https://auth');
  });

  it('is undefined when nothing is set, so devtools falls back to the env var and warns', () => {
    expect(resolveDevtoolsBaseUrl({ auth: false })).toBeUndefined();
    expect(resolveDevtoolsBaseUrl({ auth: { apiUrl: '' }, apiUrl: ' ' })).toBeUndefined();
  });
});
