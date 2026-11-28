// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { z } from 'zod';

import { resetRuntimeSlots } from './reset-runtime';

const API = 'https://api.example.test';
const PATH = '/apix/cars/';
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

let events: Array<Record<string, unknown>>;
let onNetwork: (event: Event) => void;

beforeEach(() => {
  vi.unstubAllGlobals();
  resetRuntimeSlots();
  vi.resetModules();
  events = [];
  onNetwork = (event) => events.push((event as CustomEvent).detail);
  window.addEventListener('network-error', onNetwork);
});
afterEach(() => {
  window.removeEventListener('network-error', onNetwork);
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

async function load() {
  const { configureApi } = await import('../api-origin');
  const { djangoFetch } = await import('../orval-mutator');
  const { auth } = await import('../auth');
  configureApi({ apiUrl: API });
  return { djangoFetch, auth };
}

describe('generated operation diagnostics in the browser', () => {
  it.each([400, 401, 403, 404, 409, 429])('reports final HTTP %s to console without another form toast', async status => {
    const secret = 'private-customer-value';
    const log = vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.stubGlobal('fetch', vi.fn(async () => json({ email: [secret] }, status)));
    const { djangoFetch } = await load();
    const err = await djangoFetch(PATH + '?token=' + secret, { auth: 'none' }).catch(e => e);
    expect(err).toMatchObject({ name: 'APIError', statusCode: status, fieldErrors: { email: [secret] } });
    expect(log).toHaveBeenCalledTimes(1);
    const line = String(log.mock.calls[0]?.[0]);
    expect(line).toContain(`GET ${API}${PATH}: HTTP ${status}; field errors: email`);
    expect(line).not.toContain(secret);
    expect(events).toHaveLength(0);
  });

  it('reports an HTTP server failure with a shared reference and no raw body', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.stubGlobal('fetch', vi.fn(async () => json({ detail: 'private SQL error' }, 503)));
    const { djangoFetch } = await load();
    await expect(djangoFetch(PATH, { method: 'POST' })).rejects.toMatchObject({ name: 'APIError', statusCode: 503 });
    expect(events).toHaveLength(1);
    expect(events[0]).toMatchObject({ method: 'POST', statusCode: 503, url: API + PATH, error: 'HTTP 503' });
    expect(String(log.mock.calls[0]?.[0])).toContain(events[0]?.reference);
    expect(JSON.stringify(events)).not.toContain('private SQL');
  });

  it('labels a cross-origin fetch rejection as possible CORS, not definite', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('private reason'); }));
    const { djangoFetch } = await load();
    await expect(djangoFetch(PATH)).rejects.toMatchObject({ name: 'NetworkError' });
    expect(events[0]).toMatchObject({ method: 'GET', possibly_cors: true, url: API + PATH });
    expect(String(log.mock.calls[0]?.[0])).toContain('possible CORS');
    expect(JSON.stringify(events)).not.toContain('private reason');
  });

  it('reports a broken response stream as a network failure', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const response = json({ ok: true });
    vi.spyOn(response, 'text').mockRejectedValue(new TypeError('stream reset'));
    vi.stubGlobal('fetch', vi.fn(async () => response));
    const { djangoFetch } = await load();
    await expect(djangoFetch(PATH)).rejects.toMatchObject({ name: 'NetworkError' });
    expect(events).toHaveLength(1);
  });

  it('reports HTML behind an API route as a non-JSON response', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.stubGlobal('fetch', vi.fn(async () => new Response('<html>private body</html>', {
      headers: { 'content-type': 'text/html' },
    })));
    const { djangoFetch } = await load();
    await expect(djangoFetch(PATH, { schema: z.object({ ok: z.boolean() }) })).rejects.toMatchObject({ name: 'APIError', statusCode: 200 });
    expect(events[0]).toMatchObject({ statusCode: 200, error: 'HTTP 200: response was not valid JSON' });
    expect(String(log.mock.calls[0]?.[0])).not.toContain('private body');
  });

  it('reports an unconfigured origin before fetch without logging configuration values', async () => {
    vi.stubEnv('NEXT_PUBLIC_API_URL', '');
    vi.stubEnv('NEXT_PUBLIC_API_PROXY_URL', undefined);
    vi.stubEnv('NEXT_PUBLIC_STATIC_BUILD', 'false');
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const { djangoFetch } = await import('../orval-mutator');
    await expect(djangoFetch(PATH)).rejects.toMatchObject({ name: 'APIConfigurationError' });
    expect(fetchMock).not.toHaveBeenCalled();
    expect(events[0]).toMatchObject({ url: PATH, error: 'API origin is not configured' });
    expect(log).toHaveBeenCalledTimes(1);
  });

  it('reports an explicit timeout, preserving the original exception', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const reason = new DOMException('deadline', 'TimeoutError');
    const controller = new AbortController();
    controller.abort(reason);
    vi.stubGlobal('fetch', vi.fn(async () => { throw reason; }));
    const { djangoFetch } = await load();
    await expect(djangoFetch(PATH, { signal: controller.signal })).rejects.toBe(reason);
    expect(events[0]).toMatchObject({ error: 'Request timed out' });
  });

  it('does not report ordinary caller cancellation', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const reason = new Error('navigation');
    const controller = new AbortController();
    controller.abort(reason);
    vi.stubGlobal('fetch', vi.fn(async () => { throw reason; }));
    const { djangoFetch } = await load();
    await expect(djangoFetch(PATH, { signal: controller.signal })).rejects.toBe(reason);
    expect(log).not.toHaveBeenCalled();
    expect(warn).not.toHaveBeenCalled();
    expect(events).toHaveLength(0);
  });

  it('does not report an intermediate 401 recovered by token refresh', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(json({ access: 'access-2', refresh: 'refresh-2' }))
      .mockResolvedValueOnce(json({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);
    const { djangoFetch, auth } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    await expect(djangoFetch(PATH)).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(log).not.toHaveBeenCalled();
    expect(warn).not.toHaveBeenCalled();
    expect(events).toHaveLength(0);
  });

  it('identifies the failing refresh endpoint without signing the user out', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockResolvedValueOnce(json({ detail: 'outage' }, 503)));
    const { djangoFetch, auth } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    await expect(djangoFetch(PATH)).rejects.toMatchObject({ name: 'APIError', statusCode: 503 });
    expect(events[0]).toMatchObject({
      method: 'POST', url: API + '/cfg/accounts/token/refresh/', statusCode: 503,
    });
    expect(auth.getRefreshToken()).toBe('refresh-1');
  });

  it('reports the causal refresh network endpoint, preserving the public operation error', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(json({ detail: 'expired' }, 401))
      .mockRejectedValueOnce(new TypeError('fetch failed')));
    const { djangoFetch, auth } = await load();
    auth.setSession({ access: 'access-1', refresh: 'refresh-1' });
    await expect(djangoFetch(PATH)).rejects.toMatchObject({ name: 'NetworkError', url: API + PATH });
    expect(events[0]).toMatchObject({
      method: 'POST', url: API + '/cfg/accounts/token/refresh/',
    });
    expect(auth.getRefreshToken()).toBe('refresh-1');
  });

  it('does not report a strict schema miss twice', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.stubGlobal('fetch', vi.fn(async () => json({ ok: 'wrong' })));
    const { djangoFetch } = await load();
    await expect(djangoFetch(PATH, { schema: z.object({ ok: z.boolean() }), validation: 'strict' })).rejects.toMatchObject({ name: 'ZodError' });
    expect(log).toHaveBeenCalledTimes(1);
    expect(events).toHaveLength(0);
  });
});
