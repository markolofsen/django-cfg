// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { sendBatch } from '../ingest';
import type { DevtoolsEvent } from '../types';

const EVENT = { event_type: 'JS_ERROR', message: 'boom' } as unknown as DevtoolsEvent;
const KEY = 'cfg.auth.access_token';

function stubFetch() {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 202 });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

function headersOf(fetchMock: ReturnType<typeof vi.fn>): Record<string, string> {
  return fetchMock.mock.calls[0]![1].headers as Record<string, string>;
}

function clearTokens() {
  document.cookie = `${KEY}=; Max-Age=0; path=/`;
  localStorage.removeItem(KEY);
  sessionStorage.removeItem(KEY);
}

describe('ingest sends the signed-in user', () => {
  beforeEach(clearTokens);
  afterEach(() => {
    clearTokens();
    vi.unstubAllGlobals();
  });

  it('sends no Authorization header without a token, body unchanged', async () => {
    const f = stubFetch();
    await sendBatch('https://api.example.com', [EVENT]);
    expect(headersOf(f).Authorization).toBeUndefined();
    expect(headersOf(f)['Content-Type']).toBe('application/json');
    expect(JSON.parse(f.mock.calls[0]![1].body)).toEqual({ events: [EVENT] });
  });

  it.each([
    ['cookie', () => { document.cookie = `${KEY}=tok-cookie; path=/`; }, 'tok-cookie'],
    ['localStorage', () => localStorage.setItem(KEY, 'tok-local'), 'tok-local'],
    ['sessionStorage', () => sessionStorage.setItem(KEY, 'tok-session'), 'tok-session'],
  ])('reads the token the api client stored in %s', async (_name, put, token) => {
    put();
    const f = stubFetch();
    await sendBatch('https://api.example.com', [EVENT]);
    expect(headersOf(f).Authorization).toBe(`Bearer ${token}`);
    expect(JSON.parse(f.mock.calls[0]![1].body)).toEqual({ events: [EVENT] });
  });

  it('keeps the unload flush CORS-simple: text/plain and no Authorization', async () => {
    localStorage.setItem(KEY, 'tok-local');
    const f = stubFetch();
    await sendBatch('https://api.example.com', [EVENT], true);
    expect(headersOf(f)['Content-Type']).toBe('text/plain');
    expect(headersOf(f).Authorization).toBeUndefined();
    expect(f.mock.calls[0]![1].keepalive).toBe(true);
  });
});
