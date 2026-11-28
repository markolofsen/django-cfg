import { describe, expect, it } from 'vitest';

import { backoffDelay } from './backoff';

describe('backoffDelay', () => {
  it('jitters the first retry too: anywhere from 0 to 1 s', () => {
    expect(backoffDelay(1, () => 0)).toBe(0);
    expect(backoffDelay(1, () => 0.5)).toBe(500);
    expect(backoffDelay(1, () => 1)).toBe(1_000);
  });

  it('doubles the ceiling per attempt up to 30 s', () => {
    const ceilings = [1, 2, 3, 4, 5, 6, 50].map((a) => backoffDelay(a, () => 1));
    expect(ceilings).toEqual([1_000, 2_000, 4_000, 8_000, 16_000, 30_000, 30_000]);
  });
});
