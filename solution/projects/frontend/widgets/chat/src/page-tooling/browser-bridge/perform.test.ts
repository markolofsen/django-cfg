// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { performAction } from './perform';
import type { RefResolver } from './overlay/resolve-ref';

/** A resolver over a fixed map, standing in for a snapshot's registry. */
const resolverFor = (map: Record<string, HTMLElement | null>): RefResolver => ({
  resolve: (ref) => map[ref] ?? null,
});

beforeEach(() => {
  document.body.innerHTML = '';
  // jsdom ships no IntersectionObserver, so `waitForVisible` resolves false —
  // which would make every action `not-visible`. The visibility contract is
  // asserted separately below with a stub.
  (globalThis as Record<string, unknown>).IntersectionObserver = class {
    constructor(private readonly cb: IntersectionObserverCallback) {}
    observe(el: Element) {
      this.cb(
        [{ isIntersecting: true, intersectionRatio: 1, target: el } as never],
        this as never,
      );
    }
    disconnect() {}
    unobserve() {}
    takeRecords() {
      return [];
    }
    root = null;
    rootMargin = '';
    thresholds = [];
  } as never;
});

describe('performAction', () => {
  it('fills an input so React hears the change', async () => {
    document.body.innerHTML = '<input id="email" />';
    const input = document.querySelector('input')!;
    const heard: string[] = [];
    input.addEventListener('input', () => heard.push(input.value));

    const outcome = await performAction(
      { kind: 'fill', ref: '@e1', value: 'a@b.c' },
      resolverFor({ '@e1': input }),
    );

    expect(outcome).toBe('approved');
    expect(input.value).toBe('a@b.c');
    // The event is what a framework listens to; a value set without it leaves
    // the field looking right and the app's state untouched.
    expect(heard).toEqual(['a@b.c']);
  });

  it('fills a textarea through its own prototype', async () => {
    document.body.innerHTML = '<textarea></textarea>';
    const area = document.querySelector('textarea')!;

    const outcome = await performAction(
      { kind: 'fill', ref: '@e1', value: 'hello' },
      resolverFor({ '@e1': area }),
    );

    expect(outcome).toBe('approved');
    expect(area.value).toBe('hello');
  });

  it('clicks a control', async () => {
    document.body.innerHTML = '<button>Save</button>';
    const button = document.querySelector('button')!;
    const clicked = vi.fn();
    button.addEventListener('click', clicked);

    const outcome = await performAction(
      { kind: 'click', ref: '@e1' },
      resolverFor({ '@e1': button }),
    );

    expect(outcome).toBe('approved');
    expect(clicked).toHaveBeenCalledTimes(1);
  });

  /**
   * The reason the target is resolved at approval time rather than when the
   * proposal was made: the page moves while the user reads.
   */
  it('reports stale when the ref no longer resolves', async () => {
    const outcome = await performAction(
      { kind: 'click', ref: '@e9' },
      resolverFor({}),
    );
    expect(outcome).toBe('stale');
  });

  it('reports stale when the element has left the document', async () => {
    const orphan = document.createElement('button');
    const outcome = await performAction(
      { kind: 'click', ref: '@e1' },
      resolverFor({ '@e1': orphan }),
    );
    expect(outcome).toBe('stale');
  });

  it('reports stale when there is no resolver at all', async () => {
    const outcome = await performAction({ kind: 'click', ref: '@e1' }, null);
    expect(outcome).toBe('stale');
  });

  /**
   * An approval is consent to what was on screen. A control that never became
   * visible was not part of what the user agreed to, so it is not clicked.
   */
  it('refuses to act on an element that never becomes visible', async () => {
    document.body.innerHTML = '<button>Hidden</button>';
    const button = document.querySelector('button')!;
    const clicked = vi.fn();
    button.addEventListener('click', clicked);

    (globalThis as Record<string, unknown>).IntersectionObserver = class {
      observe() {}
      disconnect() {}
      unobserve() {}
      takeRecords() {
        return [];
      }
      root = null;
      rootMargin = '';
      thresholds = [];
    } as never;

    const outcome = await performAction(
      { kind: 'click', ref: '@e1' },
      resolverFor({ '@e1': button }),
    );

    expect(outcome).toBe('not-visible');
    expect(clicked).not.toHaveBeenCalled();
  }, 2000);
});
