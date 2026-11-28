import { describe, expect, it } from 'vitest';

import { estimateTokens } from './tokens';

describe('estimateTokens', () => {
  it('returns 0 for an empty string', () => {
    expect(estimateTokens('')).toBe(0);
  });

  it('scales with length (~chars / 4.2)', () => {
    expect(estimateTokens('a'.repeat(42))).toBe(10);
  });

  it('rounds up partial tokens', () => {
    expect(estimateTokens('abc')).toBe(1);
  });
});
