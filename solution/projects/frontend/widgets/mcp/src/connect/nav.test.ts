import { describe, expect, it } from 'vitest';

import { HOME, backOf, trail } from './nav';

describe('navigation', () => {
  it('goes back to home from any screen', () => {
    expect(backOf({ kind: 'brand', id: 'cursor' })).toEqual(HOME);
    expect(backOf({ kind: 'manual' })).toEqual(HOME);
    expect(backOf(HOME)).toEqual(HOME);
  });

  it('lists the crumbs from the root', () => {
    expect(trail(HOME)).toEqual([{ kind: 'root' }]);
    expect(trail({ kind: 'brand', id: 'claude' }).map((c) => c.kind)).toEqual(['root', 'brand']);
    expect(trail({ kind: 'manual' }).map((c) => c.kind)).toEqual(['root', 'manual']);
  });
});
