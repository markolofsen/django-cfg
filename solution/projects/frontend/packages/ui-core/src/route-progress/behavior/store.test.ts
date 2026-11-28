import { describe, expect, it, vi } from 'vitest';

import { createNavigationBehaviorStore } from './store';

describe('navigation behaviour store', () => {
  it('is empty without leases', () => {
    expect(createNavigationBehaviorStore().get()).toEqual({});
  });

  it('the latest lease wins per field and a released lease is forgotten', () => {
    const s = createNavigationBehaviorStore();
    const a = s.acquire({ scroll: false, progress: false });
    const b = s.acquire({ progress: true });
    expect(s.get()).toEqual({ scroll: false, progress: true });
    b();
    expect(s.get()).toEqual({ scroll: false, progress: false });
    a();
    expect(s.get()).toEqual({});
  });

  it('releasing twice is harmless', () => {
    const s = createNavigationBehaviorStore();
    const a = s.acquire({ scroll: false });
    a();
    a();
    expect(s.get()).toEqual({});
  });

  it('notifies only when the effective value changes, and keeps the object otherwise', () => {
    const s = createNavigationBehaviorStore();
    const l = vi.fn();
    s.subscribe(l);
    const a = s.acquire({ progress: false });
    const snapshot = s.get();
    const b = s.acquire({ progress: false });
    expect(l).toHaveBeenCalledTimes(1);
    expect(s.get()).toBe(snapshot);
    b();
    a();
    expect(l).toHaveBeenCalledTimes(2);
  });

  it('stores are independent', () => {
    const one = createNavigationBehaviorStore();
    const two = createNavigationBehaviorStore();
    one.acquire({ scroll: false });
    expect(two.get()).toEqual({});
  });
});
