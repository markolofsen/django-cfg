// @vitest-environment jsdom
/**
 * H0.4 origin modes in the browser (`document` exists). The resolver reads the literal `process.env.NEXT_PUBLIC_*`
 * at call time, so `vi.stubEnv` stands in for what Next would inline. The smoke suite covers the inlining itself.
 */
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

async function loadOrigin() {
  return import('../api-origin');
}

/** The URL a request resolves to, or the error name when it cannot resolve. */
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
  vi.restoreAllMocks();
});

describe('origin modes in the browser', () => {
  it.each<[string, Env, string, string]>([
    ['the API URL set', { NEXT_PUBLIC_API_URL: API }, `${API}${PATH}`, `${API}${PATH}`],
    ['PROXY empty: same-origin', { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: '' }, PATH, `${API}${PATH}`],
    ['PROXY empty and no API URL', { NEXT_PUBLIC_API_PROXY_URL: '' }, PATH, THROWS],
    ['PROXY set', { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: PROXY }, `${PROXY}${PATH}`, `${API}${PATH}`],
    ['PROXY a path', { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: '/apix' }, `/apix${PATH}`, `${API}${PATH}`],
    ['STATIC_BUILD=true', { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_STATIC_BUILD: 'true' }, PATH, `${API}${PATH}`],
    [
      'STATIC_BUILD=true ahead of PROXY',
      { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: PROXY, NEXT_PUBLIC_STATIC_BUILD: 'true' },
      PATH,
      `${API}${PATH}`,
    ],
    ['STATIC_BUILD=true alone', { NEXT_PUBLIC_STATIC_BUILD: 'true' }, PATH, THROWS],
    ['STATIC_BUILD other than "true"', { NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_STATIC_BUILD: '1' }, `${API}${PATH}`, `${API}${PATH}`],
    ['nothing set', {}, THROWS, THROWS],
  ])('%s', async (_label, env, expected, expectedDirect) => {
    setEnv(env);
    const { hasApiOrigin, resolveApiUrl } = await loadOrigin();

    expect(attempt(() => resolveApiUrl(PATH))).toBe(expected);
    expect(attempt(() => resolveApiUrl(PATH, { origin: 'direct' }))).toBe(expectedDirect);
    // A relative mode counts as configured: the profile guard lets the request go.
    expect(hasApiOrigin()).toBe(expected !== THROWS);
    expect(hasApiOrigin({ origin: 'direct' })).toBe(expectedDirect !== THROWS);
  });

  it('sends a same-origin request through djangoFetch when PROXY is empty, and direct ones to the API host', async () => {
    setEnv({ NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: '' });
    const fetchMock = vi.fn(async () => new Response('{}', { status: 200, headers: { 'content-type': 'application/json' } }));
    vi.stubGlobal('fetch', fetchMock);
    const { djangoFetch } = await import('../orval-mutator');

    await djangoFetch(PATH);
    await djangoFetch(PATH, { origin: 'direct' });

    expect(fetchMock.mock.calls.map((call) => String((call as unknown[])[0]))).toEqual([PATH, `${API}${PATH}`]);
  });
});

describe('an explicit origin in the browser', () => {
  it('wins over the static build, the proxy and the API URL', async () => {
    setEnv({ NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: '', NEXT_PUBLIC_STATIC_BUILD: 'true' });
    const { configureApi, resolveApiUrl } = await loadOrigin();

    expect(configureApi({ apiUrl: `${CONFIGURED}/` })).toBe(CONFIGURED);

    expect(resolveApiUrl(PATH)).toBe(`${CONFIGURED}${PATH}`);
    expect(resolveApiUrl(PATH, { origin: 'direct' })).toBe(`${CONFIGURED}${PATH}`);
  });

  it('keeps a path prefix of an absolute origin', async () => {
    const { configureApi, resolveApiUrl } = await loadOrigin();
    configureApi({ apiUrl: 'https://example.test/backend/?x=1#y' });

    expect(resolveApiUrl(PATH)).toBe(`https://example.test/backend${PATH}`);
  });

  it('accepts a same-origin prefix such as /apix; a direct request skips it for the API host', async () => {
    setEnv({ NEXT_PUBLIC_API_URL: API });
    const { configureApi, hasApiOrigin, resolveApiUrl, setApiOrigin } = await loadOrigin();

    expect(configureApi({ apiUrl: '/apix/' })).toBe('/apix');
    expect(resolveApiUrl(PATH)).toBe(`/apix${PATH}`);
    expect(resolveApiUrl(PATH, { origin: 'direct' })).toBe(`${API}${PATH}`);
    expect(hasApiOrigin()).toBe(true);

    expect(setApiOrigin('/')).toBe('');
    expect(resolveApiUrl(PATH)).toBe(PATH);
  });

  it.each([null, '', '   '])('%j clears an earlier value, so the environment decides again', async (cleared) => {
    setEnv({ NEXT_PUBLIC_API_URL: API, NEXT_PUBLIC_API_PROXY_URL: '' });
    const { configureApi, resolveApiUrl } = await loadOrigin();
    configureApi({ apiUrl: CONFIGURED });

    configureApi({ apiUrl: cleared });

    expect(resolveApiUrl(PATH)).toBe(PATH);
  });

  it.each(['api.example.test', 'ftp://api.example.test', '//api.example.test', 'https://'])(
    'never throws for the invalid value %j: one warning, and the previous origin stays',
    async (invalid) => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { configureApi, resolveApiUrl, setApiOrigin } = await loadOrigin();
      configureApi({ apiUrl: CONFIGURED });

      expect(() => configureApi({ apiUrl: invalid })).not.toThrow();
      expect(() => configureApi({ apiUrl: invalid })).not.toThrow();
      expect(() => setApiOrigin(invalid)).not.toThrow();

      expect(resolveApiUrl(PATH)).toBe(`${CONFIGURED}${PATH}`);
      // Once for configureApi (called on every AuthProvider render), once for setApiOrigin.
      expect(warn).toHaveBeenCalledTimes(2);
    },
  );

  it('falls back to same-origin relative only with allowRelative', async () => {
    const { configureApi, hasApiOrigin, resolveApiUrl } = await loadOrigin();
    expect(hasApiOrigin()).toBe(false);

    configureApi({ allowRelative: true });

    expect(hasApiOrigin()).toBe(true);
    expect(resolveApiUrl(PATH)).toBe(PATH);
    expect(attempt(() => resolveApiUrl(PATH, { origin: 'direct' }))).toBe(THROWS);
  });
});
