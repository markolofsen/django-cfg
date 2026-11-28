import { afterEach, describe, expect, it, vi } from 'vitest';

import { resolveMcpServer } from './server';

describe('resolveMcpServer', () => {
  afterEach(() => vi.unstubAllEnvs());

  it('derives the default endpoint from the public API origin', () => {
    vi.stubEnv('NEXT_PUBLIC_API_URL', 'https://api.example.com');

    expect(resolveMcpServer()).toMatchObject({
      url: 'https://api.example.com/cfg/mcp/',
      alias: 'example',
      name: 'Example',
    });
  });

  it('keeps an explicit server URL independent of the host API origin', () => {
    vi.stubEnv('NEXT_PUBLIC_API_URL', 'https://api.example.com');

    expect(resolveMcpServer({ url: 'https://mcp.other.test/root' }).url).toBe('https://mcp.other.test/root/');
  });
});
