import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createProgressEngine } from './createProgressEngine';

beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

describe('progress engine', () => {
  it('starts at the minimum and trickles forward', () => {
    const e = createProgressEngine();
    e.start();
    expect(e.getState()).toEqual({ phase: 'running', value: 0.08 });
    vi.advanceTimersByTime(200);
    expect(e.getState().value).toBeCloseTo(0.18);
  });

  it('never reaches 1 on its own', () => {
    const e = createProgressEngine({ maxMs: 1e9 });
    e.start();
    vi.advanceTimersByTime(600_000);
    expect(e.getState().value).toBeLessThanOrEqual(0.994);
  });

  it('starting while running keeps the value and the single timer', () => {
    const e = createProgressEngine();
    e.start();
    vi.advanceTimersByTime(200);
    const v = e.getState().value;
    e.start();
    expect(e.getState().value).toBe(v);
  });

  it('done fills the bar, then goes idle after finishMs', () => {
    const e = createProgressEngine({ finishMs: 400 });
    e.start();
    e.done();
    expect(e.getState()).toEqual({ phase: 'finishing', value: 1 });
    vi.advanceTimersByTime(399);
    expect(e.getState().phase).toBe('finishing');
    vi.advanceTimersByTime(1);
    expect(e.getState().phase).toBe('idle');
    expect(vi.getTimerCount()).toBe(0);
  });

  it('done while idle does nothing', () => {
    const e = createProgressEngine();
    const l = vi.fn();
    e.subscribe(l);
    e.done();
    expect(l).not.toHaveBeenCalled();
  });

  it('a run nobody finished ends at the ceiling', () => {
    const e = createProgressEngine({ maxMs: 5000, finishMs: 100 });
    e.start();
    vi.advanceTimersByTime(5000);
    expect(e.getState().phase).toBe('finishing');
    vi.advanceTimersByTime(100);
    expect(e.getState().phase).toBe('idle');
  });

  it('cancel drops the run at once and clears every timer', () => {
    const e = createProgressEngine();
    e.start();
    e.cancel();
    expect(e.getState().phase).toBe('idle');
    expect(vi.getTimerCount()).toBe(0);
  });

  it('a new run can start during the fade-out', () => {
    const e = createProgressEngine();
    e.start();
    e.done();
    e.start();
    expect(e.getState()).toEqual({ phase: 'running', value: 0.08 });
    vi.advanceTimersByTime(1000);
    expect(e.getState().phase).toBe('running');
  });

  it('set clamps and ignores calls while idle', () => {
    const e = createProgressEngine();
    e.set(0.5);
    expect(e.getState().phase).toBe('idle');
    e.start();
    e.set(5);
    expect(e.getState().value).toBe(0.994);
    e.set(-1);
    expect(e.getState().value).toBe(0);
  });

  it('subscribers get a new snapshot object per change and can unsubscribe', () => {
    const e = createProgressEngine();
    const seen: unknown[] = [];
    const off = e.subscribe(() => seen.push(e.getState()));
    e.start();
    e.inc();
    off();
    e.inc();
    expect(seen).toHaveLength(2);
    expect(seen[0]).not.toBe(seen[1]);
  });
});
