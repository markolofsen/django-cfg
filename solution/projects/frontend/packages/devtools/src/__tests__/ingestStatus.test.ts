// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

/**
 * `devtools.status()`, the no-baseUrl warning and `devtools.ping()`.
 * Modules are re-imported per test: the warning is once per page load and the
 * store is a singleton.
 */
async function load() {
  vi.resetModules();
  return (await import('../instance')).devtools;
}

describe('devtools ingest diagnostics', () => {
  let warn: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.stubEnv('NEXT_PUBLIC_API_URL', '');
    // rawConsole binds console.warn at import time, so spy before importing.
    warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('warns once, loudly, when ingest is on and no base URL resolves', async () => {
    const devtools = await load();
    devtools.init({ captureConsole: false });
    devtools.destroy();
    devtools.init({ captureConsole: false });
    devtools.destroy();

    const calls = warn.mock.calls.filter((c: unknown[]) => String(c[0]).includes('[devtools]'));
    expect(calls).toHaveLength(1);
    expect(String(calls[0]?.[0])).toContain('baseUrl');
    expect(String(calls[0]?.[0])).toContain('NEXT_PUBLIC_API_URL');
  });

  it('does not warn when ingest is off or a baseUrl is given', async () => {
    const devtools = await load();
    devtools.init({ ingest: false, captureConsole: false });
    devtools.destroy();
    devtools.init({ baseUrl: 'https://api.example.com', captureConsole: false });
    devtools.destroy();
    expect(warn.mock.calls.filter((c: unknown[]) => String(c[0]).includes('[devtools]'))).toHaveLength(0);
  });

  it('status() reports a dropped event when there is no base URL', async () => {
    const devtools = await load();
    devtools.init({ captureConsole: false });
    devtools.error('boom');
    await devtools.ping();
    const s = devtools.status();
    devtools.destroy();
    expect(s.ingest).toBe(true);
    expect(s.baseUrl).toBe('');
    expect(s.sent).toBe(0);
    expect(s.failed).toBeGreaterThan(0);
    expect(s.lastError).toContain('no baseUrl');
  });

  it('ping() posts one info event to the ingest endpoint and status() counts it', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 202 });
    vi.stubGlobal('fetch', fetchMock);
    const devtools = await load();
    devtools.init({ baseUrl: 'https://api.example.com', captureConsole: false });

    const s = await devtools.ping();
    devtools.destroy();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://api.example.com/cfg/monitor/ingest/');
    const { events } = JSON.parse(String(init.body));
    expect(events).toHaveLength(1);
    expect(events[0].message).toBe('devtools ping');
    expect(events[0].level).toBe('info');
    expect(s).toMatchObject({ ingest: true, baseUrl: 'https://api.example.com', queued: 0, sent: 1, failed: 0, lastError: null, circuitOpen: false });
    expect(s.lastSentAt).toBeTypeOf('number');
  });

  it('status() records a failed send and keeps the events queued', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 502 }));
    const devtools = await load();
    devtools.init({ baseUrl: 'https://api.example.com', captureConsole: false });
    const s = await devtools.ping();
    devtools.destroy();
    expect(s.sent).toBe(0);
    expect(s.failed).toBe(1);
    expect(s.queued).toBe(1);
    expect(s.lastError).toBe('ingest 502');
  });
});
