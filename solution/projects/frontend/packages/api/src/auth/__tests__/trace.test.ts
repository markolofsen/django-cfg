// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from 'vitest';

import { authTrace, clearAuthTrace, dumpAuthTrace, readAuthTrace, registerAuthCopy } from '../trace';

describe('auth trace', () => {
  beforeEach(() => {
    localStorage.clear();
    clearAuthTrace();
  });

  it('loading the module does not count a copy; registerAuthCopy does, and a second one is a dup', () => {
    const g = globalThis as Record<string, unknown>;
    delete g.__cfgAuthCopies;
    registerAuthCopy();
    expect(g.__cfgAuthCopies).toBe(1);
    expect(readAuthTrace().some((e) => e.ev === 'dup.copy')).toBe(false);
    registerAuthCopy();
    expect(g.__cfgAuthCopies).toBe(2);
    expect(readAuthTrace().some((e) => e.ev === 'dup.copy')).toBe(true);
    delete g.__cfgAuthCopies;
  });

  it('drops sensitive keys and cuts long strings', () => {
    authTrace('x', { token: 'abc', email: 'a@b.c', otp: '123456', path: '/auth', long: 'y'.repeat(300), ok: true });
    const f = readAuthTrace()[0]!.f!;
    expect(Object.keys(f).sort()).toEqual(['long', 'ok', 'path']);
    expect((f.long as string).length).toBeLessThan(130);
    expect(localStorage.getItem('cfg.auth.trace')).not.toContain('123456');
  });

  it('collapses an identical repeat so a loop cannot flush the start of the chain', () => {
    authTrace('start');
    for (let i = 0; i < 500; i++) authTrace('guard.redirect', { from: '/', to: '/auth' });
    const t = readAuthTrace();
    expect(t.map((e) => e.ev)).toEqual(['start', 'guard.redirect']);
    expect(t[1]!.n).toBe(500);
    expect(dumpAuthTrace()).toContain('x500');
  });

  it('keeps at most 200 distinct events', () => {
    for (let i = 0; i < 300; i++) authTrace('e', { i });
    expect(readAuthTrace()).toHaveLength(200);
  });

  it('survives in storage for the next page', () => {
    authTrace('a');
    expect(JSON.parse(localStorage.getItem('cfg.auth.trace')!)).toHaveLength(1);
  });
});
