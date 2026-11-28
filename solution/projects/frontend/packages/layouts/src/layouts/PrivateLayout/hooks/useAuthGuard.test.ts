import { beforeEach, describe, expect, it } from 'vitest';

import { redirectLoopDetected, resetRedirectLoop } from './useAuthGuard';

describe('guard redirect circuit breaker', () => {
  beforeEach(resetRedirectLoop);

  it('allows a few redirects', () => {
    for (let i = 0; i < 5; i++) expect(redirectLoopDetected(1000 + i * 400)).toBe(false);
  });

  it('trips on the sixth redirect inside the window', () => {
    for (let i = 0; i < 5; i++) redirectLoopDetected(1000 + i * 400);
    expect(redirectLoopDetected(3500)).toBe(true);
  });

  it('forgets redirects older than the window (a slow, legitimate sequence never trips)', () => {
    for (let i = 0; i < 20; i++) expect(redirectLoopDetected(i * 6000)).toBe(false);
  });
});
