import { describe, expect, it, vi } from 'vitest';

describe('sharedContext', () => {
  it('returns one context object for a key, even from a second module copy', async () => {
    const a = await import('../context/sharedContext');
    vi.resetModules();
    const b = await import('../context/sharedContext');
    expect(a.sharedContext).not.toBe(b.sharedContext);
    expect(a.sharedContext('k', 1)).toBe(b.sharedContext('k', 2));
  });

  it('keeps different keys apart', async () => {
    const { sharedContext } = await import('../context/sharedContext');
    expect(sharedContext('x', 1)).not.toBe(sharedContext('y', 1));
  });
});
