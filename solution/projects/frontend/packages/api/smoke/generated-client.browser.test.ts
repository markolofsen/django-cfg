// @vitest-environment jsdom
/**
 * The generated client in a browser page (H2.1). Calls the generated `cfgAccountsProfileRetrieve`, never
 * `djangoFetch` directly: what is under test is the generated module, its shim and the runtime together.
 *
 * A case named after a plan item (`H0.6`, `H0.7`) is expected to fail (`it.fails`) until the runtime owner ships
 * that item. When it starts to pass, vitest reports it as failing: turn it into a plain `it`.
 */
import { beforeEach, describe, expect, it } from 'vitest';

import {
  CONFIGURED_ORIGIN,
  ENV_ORIGIN,
  PROFILE_PATH,
  REFRESH_PATH,
  USER,
  USER_OFF_CONTRACT,
  json,
  loadClient,
  requestHeaders,
  requestInit,
  requestUrl,
  resetPage,
  stubFetch,
  unreachable,
} from './harness';

beforeEach(resetPage);

describe('generated client in the browser: where requests go', () => {
  it('sends a generated operation to the origin built in as NEXT_PUBLIC_API_URL', async () => {
    const fetchMock = stubFetch(json(USER));
    const { cfgAccountsProfileRetrieve } = await loadClient();

    await expect(cfgAccountsProfileRetrieve()).resolves.toEqual(USER);

    expect(requestUrl(fetchMock, 0)).toBe(`${ENV_ORIGIN}${PROFILE_PATH}`);
  });

  it.each(['configureApi', 'setApiOrigin'] as const)(
    'sends it to the origin given to %s, ahead of the built-in one',
    async (setter) => {
      const fetchMock = stubFetch(json(USER));
      const client = await loadClient();
      if (setter === 'configureApi') client.configureApi({ apiUrl: CONFIGURED_ORIGIN });
      else client.setApiOrigin(CONFIGURED_ORIGIN);

      await client.cfgAccountsProfileRetrieve();

      expect(requestUrl(fetchMock, 0)).toBe(`${CONFIGURED_ORIGIN}${PROFILE_PATH}`);
    },
  );
});

describe('generated client in the browser: what every request carries', () => {
  it('sends Accept-Language from the route locale and one X-Client-Id per browser', async () => {
    document.cookie = 'NEXT_LOCALE=de; Path=/';
    const fetchMock = stubFetch(json(USER), json(USER));
    const { cfgAccountsProfileRetrieve } = await loadClient();

    await cfgAccountsProfileRetrieve();
    await cfgAccountsProfileRetrieve();

    const first = requestHeaders(fetchMock, 0);
    expect(first.get('Accept-Language')).toBe('de');
    expect(first.get('X-Client-Id')).toMatch(/\S/);
    expect(requestHeaders(fetchMock, 1).get('X-Client-Id')).toBe(first.get('X-Client-Id'));
  });

  it('attaches the Bearer token held by the auth store', async () => {
    const fetchMock = stubFetch(json(USER));
    const { auth, cfgAccountsProfileRetrieve } = await loadClient();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await cfgAccountsProfileRetrieve();

    expect(requestHeaders(fetchMock, 0).get('Authorization')).toBe('Bearer access-1');
  });
});

describe('generated client in the browser: an expired access token', () => {
  it('answers a 401 with one refresh and one retry that carries the new token', async () => {
    const fetchMock = stubFetch(
      json({ detail: 'Token is expired' }, 401),
      json({ access: 'access-2', refresh: 'refresh-2' }),
      json(USER),
    );
    const { auth, cfgAccountsProfileRetrieve } = await loadClient();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await expect(cfgAccountsProfileRetrieve()).resolves.toEqual(USER);

    expect(fetchMock.mock.calls.map((_, index) => requestUrl(fetchMock, index))).toEqual([
      `${ENV_ORIGIN}${PROFILE_PATH}`,
      `${ENV_ORIGIN}${REFRESH_PATH}`,
      `${ENV_ORIGIN}${PROFILE_PATH}`,
    ]);
    expect(requestInit(fetchMock, 1).method).toBe('POST');
    expect(JSON.parse(String(requestInit(fetchMock, 1).body))).toEqual({ refresh: 'refresh-1' });
    expect(requestHeaders(fetchMock, 2).get('Authorization')).toBe('Bearer access-2');
    expect(auth.getToken()).toBe('access-2');
  });

  it('does not refresh a second time when the retry is still 401', async () => {
    const fetchMock = stubFetch(
      json({ detail: 'Token is expired' }, 401),
      json({ access: 'access-2', refresh: 'refresh-2' }),
      json({ detail: 'Not allowed' }, 401),
    );
    const { APIError, auth, cfgAccountsProfileRetrieve } = await loadClient();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    const failure = await cfgAccountsProfileRetrieve().catch((error: unknown) => error);

    expect(failure).toBeInstanceOf(APIError);
    expect((failure as InstanceType<typeof APIError>).statusCode).toBe(401);
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });
});

describe('generated client in the browser: a response that misses its schema (soft Zod)', () => {
  it('dispatches the zod-validation-error window event', async () => {
    stubFetch(json(USER_OFF_CONTRACT));
    const { cfgAccountsProfileRetrieve } = await loadClient();
    const seen: CustomEvent[] = [];
    const listener = (event: Event) => seen.push(event as CustomEvent);
    window.addEventListener('zod-validation-error', listener);

    try {
      await cfgAccountsProfileRetrieve().catch(() => undefined);
    } finally {
      window.removeEventListener('zod-validation-error', listener);
    }

    expect(seen).toHaveLength(1);
    expect(seen[0]?.detail).toMatchObject({
      method: 'GET',
      path: PROFILE_PATH,
      response: USER_OFF_CONTRACT,
    });
  });

  // Owner decision 2026-11-23: a schema miss is reported, and the page keeps the data the server sent.
  it('H0.6: still returns the data the server sent', async () => {
    stubFetch(json(USER_OFF_CONTRACT));
    const { cfgAccountsProfileRetrieve } = await loadClient();

    await expect(cfgAccountsProfileRetrieve()).resolves.toEqual(USER_OFF_CONTRACT);
  });
});

describe('generated client in the browser: the API host is unreachable', () => {
  it('rejects with NetworkError and keeps the session', async () => {
    const fetchMock = stubFetch(unreachable());
    const { NetworkError, auth, cfgAccountsProfileRetrieve } = await loadClient();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await expect(cfgAccountsProfileRetrieve()).rejects.toBeInstanceOf(NetworkError);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(auth.isAuthenticated()).toBe(true);
    expect([auth.getToken(), auth.getRefreshToken()]).toEqual(['access-1', 'refresh-1']);
  });

  // Audit E10: the host goes away between the 401 and the refresh. A transport failure is not a sign-out.
  it('H0.7: keeps the session when the refresh cannot reach the host', async () => {
    stubFetch(json({ detail: 'Token is expired' }, 401), unreachable());
    const { auth, cfgAccountsProfileRetrieve } = await loadClient();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });

    await cfgAccountsProfileRetrieve().catch(() => undefined);

    expect(auth.getRefreshToken()).toBe('refresh-1');
  });
});
