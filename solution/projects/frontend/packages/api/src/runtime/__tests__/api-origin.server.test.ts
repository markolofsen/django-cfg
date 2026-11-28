/**
 * H0.4 origin modes on the server (node: no `document`). The server takes an explicit absolute origin, else
 * `NEXT_PUBLIC_API_URL`. It ignores the proxy and the static build: a proxy would be a round trip to itself, and
 * Node's `fetch` cannot take a relative URL.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { resetRuntimeSlots } from './reset-runtime';

const API = 'https://api.env.test';
const PROXY = 'https://proxy.env.test';
const CONFIGURED = 'https://api.configured.test';
const PATH = '/cfg/accounts/profile/';
const THROWS = 'APIConfigurationError';

type Env = {
  NEXT_PUBLIC_API_URL?: string;
  NEXT_PUBLIC_API_PROXY_URL?: string;
  NEXT_PUBLIC_STATIC_BUILD?: string;
};

function setEnv(env: Env): void {
  vi.stubEnv('NEXT_PUBLIC_API_URL', env.NEXT_PUBLIC_API_URL);
  vi.stubEnv('NEXT_PUBLIC_API_PROXY_URL', env.NEXT_PUBLIC_API_PROXY_URL);
  vi.stubEnv('NEXT_PUBLIC_STATIC_BUILD', env.NEXT_PUBLIC_STATIC_BUILD);
}

function attempt(resolve: () => string): string {
  try {
    return resolve();
  } catch (error) {
    return (error as Error).name;
  }
}

beforeEach(() => {
  vi.unstubAllGlobals();
  resetRuntimeSlots();
  vi.resetModules();
});

afterEach(() => {
  vi.unstubAllEnvs();
});

describe('origin modes on the server', () => {
  it('runs without a document', () => {
    expect(typeof document).toBe('undefined');
  });

  it.each<[string, Env, string]>([
    ['the API URL set', { NEXT_PUBLIC_API_URL: API }, `${API}${PATH}`],
    ['PROXY empty is ignored', { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: '' }, `${API}${PATH}`],
    ['PROXY set is ignored', { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: PROXY }, `${API}${PATH}`],
    ['STATIC_BUILD=true is ignored', { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_STATIC_BUILD: 'true' }, `${API}${PATH}`],
    ['PROXY empty and no API URL', { NEXT_PUBLIC_API_PROXY_URL: '' }, THROWS],
    ['PROXY set and no API URL', { NEXT_PUBLIC_API_PROXY_URL: PROXY }, THROWS],
    ['STATIC_BUILD=true alone', { NEXT_PUBLIC_STATIC_BUILD: 'true' }, THROWS],
    ['nothing set', {}, THROWS],
  ])('%s', async (_label, env, expected) => {
    setEnv(env);
    const { hasApiOrigin, resolveApiUrl } = await import('../api-origin');

    expect(attempt(() => resolveApiUrl(PATH))).toBe(expected);
    expect(attempt(() => resolveApiUrl(PATH, { origin: 'direct' }))).toBe(expected);
    expect(hasApiOrigin()).toBe(expected !== THROWS);
  });

  it('prefers an explicit absolute origin', async () => {
    setEnv({ NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: '' });
    const { configureApi, resolveApiUrl } = await import('../api-origin');
    configureApi({ apiUrl: CONFIGURED });

    expect(resolveApiUrl(PATH)).toBe(`${CONFIGURED}${PATH}`);
  });

  it('skips an explicit same-origin prefix for NEXT_PUBLIC_API_URL', async () => {
    const { configureApi, resolveApiUrl } = await import('../api-origin');
    configureApi({ apiUrl: '/apix' });
    expect(attempt(() => resolveApiUrl(PATH))).toBe(THROWS);

    setEnv({ NEXT_PUBLIC_API_URL: API });
    expect(resolveApiUrl(PATH)).toBe(`${API}${PATH}`);
  });

  it('rejects an unconfigured operation before fetch', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const { APIConfigurationError } = await import('../errors');
    const { djangoFetch } = await import('../orval-mutator');

    await expect(djangoFetch(PATH)).rejects.toBeInstanceOf(APIConfigurationError);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe('how the resolver reads the environment', () => {
  // Next inlines only the literal member expression; any other form is empty in the browser (H0.1).
  const source = readFileSync(fileURLToPath(new URL('../api-origin.ts', import.meta.url)), 'utf8')
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/\/\/.*$/gm, '');

  it('never reads globalThis.process', () => {
    expect(source).not.toMatch(/globalThis\s*\.\s*process/);
  });

  it('reads process.env only as the three literal NEXT_PUBLIC names', () => {
    const reads = source.match(/process\s*\.\s*env\b[^;)]*/g) ?? [];
    expect(reads.length).toBeGreaterThan(0);
    for (const read of reads) {
      expect(read).toMatch(/^process\.env\.NEXT_PUBLIC_(?:API_URL|API_PROXY_URL|STATIC_BUILD)\b/);
    }
  });
});
