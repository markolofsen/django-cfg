import { afterEach, describe, expect, it, vi } from 'vitest';

import { resolveRealtimeApiUrl } from './realtimeApiUrl';

afterEach(() => {
  vi.unstubAllEnvs();
});

describe('resolveRealtimeApiUrl', () => {
  it('prefers realtime.apiUrl, then apiUrl, then auth.apiUrl', () => {
    const auth = { apiUrl: 'https://auth.example.com' };
    expect(resolveRealtimeApiUrl({ realtime: { apiUrl: 'https://rt.example.com' }, apiUrl: 'https://a.example.com', auth })).toBe(
      'https://rt.example.com',
    );
    expect(resolveRealtimeApiUrl({ apiUrl: 'https://a.example.com', auth })).toBe('https://a.example.com');
    expect(resolveRealtimeApiUrl({ auth })).toBe('https://auth.example.com');
  });

  it('falls back to NEXT_PUBLIC_API_URL, then to nothing', () => {
    vi.stubEnv('NEXT_PUBLIC_API_URL', 'https://env.example.com');
    expect(resolveRealtimeApiUrl({ auth: false, apiUrl: ' ' })).toBe('https://env.example.com');
    vi.stubEnv('NEXT_PUBLIC_API_URL', '');
    expect(resolveRealtimeApiUrl({ auth: false })).toBeUndefined();
  });
});
