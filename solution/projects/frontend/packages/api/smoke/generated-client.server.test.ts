/**
 * The generated client on the server (SSR, route handlers, scripts): node, no `window`, no `document` (H2.1).
 * Node 21+ defines `navigator.language`, so this is also the case that keeps the host's own locale out of
 * `Accept-Language`. The server has no reader locale to send.
 */
import { beforeEach, describe, expect, it } from 'vitest';

import { ENV_ORIGIN, PROFILE_PATH, USER, json, loadClient, requestHeaders, requestUrl, resetPage, stubFetch } from './harness';

beforeEach(resetPage);

describe('generated client on the server', () => {
  it('sends a generated operation to the origin built in as NEXT_PUBLIC_API_URL', async () => {
    const fetchMock = stubFetch(json(USER));
    const { cfgAccountsProfileRetrieve } = await loadClient();

    await expect(cfgAccountsProfileRetrieve()).resolves.toEqual(USER);

    expect(requestUrl(fetchMock, 0)).toBe(`${ENV_ORIGIN}${PROFILE_PATH}`);
  });

  it('sends no Accept-Language', async () => {
    const fetchMock = stubFetch(json(USER));
    const { cfgAccountsProfileRetrieve } = await loadClient();

    await cfgAccountsProfileRetrieve();

    expect(requestHeaders(fetchMock, 0).has('Accept-Language')).toBe(false);
  });
});
