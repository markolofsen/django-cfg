import { describe, expect, it } from 'vitest';

import { newSegmentId } from '../core/ids';

describe('newSegmentId', () => {
  it('produces unique values across calls', () => {
    const ids = new Set<string>();
    for (let i = 0; i < 200; i += 1) ids.add(newSegmentId());
    expect(ids.size).toBe(200);
  });

  it('matches the seg_<time>_<n> shape', () => {
    expect(newSegmentId()).toMatch(/^seg_[a-z0-9]+_[a-z0-9]+$/);
  });
});
