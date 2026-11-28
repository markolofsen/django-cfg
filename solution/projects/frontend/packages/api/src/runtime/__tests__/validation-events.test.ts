// @vitest-environment jsdom
/**
 * Soft Zod (H0.6, owner decision 2026-11-23): a response that misses its schema is reported through the
 * `zod-validation-error` window event and returned as the server sent it. Only `validation: 'strict'` rejects.
 * A 2xx body that is not JSON is a transport problem and rejects as `APIError` (audit E7).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { z } from 'zod';

import { resetRuntimeSlots } from './reset-runtime';

const TITLES = '/apix/catalog/v1/titles/';
const schema = z.object({ ok: z.boolean() });

const reply = (body: string, contentType: string) =>
  vi.fn(async () => new Response(body, { status: 200, headers: { 'content-type': contentType } }));

describe('generated response validation diagnostics', () => {
  afterEach(() => vi.restoreAllMocks());

  beforeEach(async () => {
    vi.unstubAllGlobals();
    resetRuntimeSlots();
    vi.resetModules();
    const { configureApi } = await import('../api-origin');
    configureApi({ apiUrl: 'https://api.example.test', allowRelative: false });
  });

  it('emits a validation event and returns the data the server sent', async () => {
    vi.stubGlobal('fetch', reply(JSON.stringify({ ok: 'not-a-boolean' }), 'application/json'));

    const { onValidationError } = await import('../validation-events');
    const { djangoFetch } = await import('../orval-mutator');
    const events: Array<{ operation: string; path: string; method: string; response: unknown }> = [];
    const unsubscribe = onValidationError((detail) => events.push(detail));

    await expect(djangoFetch(TITLES, { schema })).resolves.toEqual({ ok: 'not-a-boolean' });
    unsubscribe();

    expect(events).toHaveLength(1);
    expect(events[0]).toMatchObject({
      operation: `GET ${TITLES}`,
      path: TITLES,
      method: 'GET',
      response: { ok: 'not-a-boolean' },
    });
  });

  it('prints safe schema diagnostics and shares the support reference with the event', async () => {
    const log = vi.spyOn(console, 'error').mockImplementation(() => {});
    const secret = 'private-customer-secret';
    const payload = { email: secret, slug: '구기' };
    vi.stubGlobal('fetch', reply(JSON.stringify(payload), 'application/json'));
    const { onValidationError } = await import('../validation-events');
    const { djangoFetch } = await import('../orval-mutator');
    const events: Array<{ reference?: string; diagnostic?: string }> = [];
    const unsubscribe = onValidationError(detail => events.push(detail));
    const invalid = z.object({
      email: z.string().refine(() => false, { message: secret }),
      slug: z.string().regex(/^[-a-zA-Z0-9_]+$/),
    });

    await expect(djangoFetch(TITLES + '?token=' + secret, { schema: invalid })).resolves.toEqual(payload);
    unsubscribe();

    expect(log).toHaveBeenCalledTimes(1);
    const line = String(log.mock.calls[0]?.[0]);
    expect(events).toHaveLength(1);
    expect(events[0]?.reference).toMatch(/^ERR-[A-Z0-9]+$/);
    expect(line).toContain(events[0]?.reference);
    expect(line).toContain('GET ' + TITLES);
    expect(line).toContain('slug: invalid_format');
    expect(line).toContain('format=regex');
    expect(line).toContain('email: custom');
    expect(line).not.toContain(secret);
    expect(line).not.toContain('구기');
    expect(events[0]?.diagnostic).not.toContain(secret);
  });

  it("keeps the ZodError rejection, after the event, for validation: 'strict'", async () => {
    vi.stubGlobal('fetch', reply(JSON.stringify({ ok: 'not-a-boolean' }), 'application/json'));

    const { onValidationError } = await import('../validation-events');
    const { djangoFetch } = await import('../orval-mutator');
    const events: unknown[] = [];
    const unsubscribe = onValidationError((detail) => events.push(detail));

    await expect(djangoFetch(TITLES, { schema, validation: 'strict' })).rejects.toMatchObject({ name: 'ZodError' });
    unsubscribe();

    expect(events).toHaveLength(1);
  });

  it('returns the parsed data, with no event, when the response matches', async () => {
    vi.stubGlobal('fetch', reply(JSON.stringify({ ok: true }), 'application/json'));

    const { onValidationError } = await import('../validation-events');
    const { djangoFetch } = await import('../orval-mutator');
    const events: unknown[] = [];
    const unsubscribe = onValidationError((detail) => events.push(detail));

    await expect(djangoFetch(TITLES, { schema })).resolves.toEqual({ ok: true });
    unsubscribe();

    expect(events).toHaveLength(0);
  });

  it('rejects a 2xx HTML page as APIError with status and URL, not as a schema miss', async () => {
    vi.stubGlobal('fetch', reply('<!doctype html><title>Not the API</title>', 'text/html; charset=utf-8'));

    const { onValidationError } = await import('../validation-events');
    const { APIError } = await import('../errors');
    const { djangoFetch } = await import('../orval-mutator');
    const events: unknown[] = [];
    const unsubscribe = onValidationError((detail) => events.push(detail));

    const failure = await djangoFetch(TITLES, { schema }).catch((error: unknown) => error);
    unsubscribe();

    expect(failure).toBeInstanceOf(APIError);
    expect(failure).toMatchObject({ statusCode: 200, url: `https://api.example.test${TITLES}` });
    expect(events).toHaveLength(0);
  });

  it('accepts a text body when the schema itself takes a string', async () => {
    vi.stubGlobal('fetch', reply('plain words', 'text/plain'));

    const { djangoFetch } = await import('../orval-mutator');

    await expect(djangoFetch(TITLES, { schema: z.string() })).resolves.toBe('plain words');
  });
});
