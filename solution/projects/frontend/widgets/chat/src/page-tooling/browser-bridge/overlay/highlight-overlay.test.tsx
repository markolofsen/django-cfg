// @vitest-environment jsdom
import { act, createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { HighlightOverlay } from './highlight-overlay';
import type { RefResolver } from './resolve-ref';
import type { CSTRefId, PointDirective } from './types';

(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true;

// jsdom has no ResizeObserver — the overlay observes its targets, so
// provide a no-op stub for the test environment.
if (typeof globalThis.ResizeObserver === 'undefined') {
  (globalThis as Record<string, unknown>).ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

// jsdom has no IntersectionObserver — the overlay uses it to wait for
// an off-screen target to become visible. Stub it to report the
// observed element as immediately intersecting so the wait resolves.
if (typeof globalThis.IntersectionObserver === 'undefined') {
  (globalThis as Record<string, unknown>).IntersectionObserver = class {
    private cb: (entries: unknown[]) => void;
    constructor(cb: (entries: unknown[]) => void) {
      this.cb = cb;
    }
    observe(target: Element) {
      this.cb([
        { target, isIntersecting: true, intersectionRatio: 1 },
      ]);
    }
    unobserve() {}
    disconnect() {}
  };
}

let container: HTMLDivElement;
let root: Root;

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
  document.body.innerHTML = '';
});

/** Resolver over a fixed map. */
function makeResolver(map: Record<string, HTMLElement | null>): RefResolver {
  return { resolve: (ref: CSTRefId) => map[ref] ?? null };
}

async function render(
  directives: PointDirective[],
  resolver: RefResolver | null,
) {
  await act(async () => {
    root.render(
      createElement(HighlightOverlay, { directives, resolver, ttlMs: 0 }),
    );
  });
}

describe('HighlightOverlay', () => {
  it('renders nothing with no directives', async () => {
    await render([], null);
    expect(document.querySelector('[data-chat-highlight-overlay]')).toBeNull();
  });

  it('renders nothing when refs do not resolve', async () => {
    await render([{ type: 'point', ref: '@e9' }], makeResolver({}));
    expect(document.querySelector('[data-chat-highlight-overlay]')).toBeNull();
  });

  it('draws the overlay for a resolved ref', async () => {
    const el = document.createElement('button');
    el.textContent = 'Save';
    document.body.appendChild(el);

    await render(
      [{ type: 'point', ref: '@e1' }],
      makeResolver({ '@e1': el }),
    );
    expect(
      document.querySelector('[data-chat-highlight-overlay]'),
    ).not.toBeNull();
    // The SVG spotlight canvas is mounted.
    expect(document.querySelector('svg')).not.toBeNull();
  });

  it('renders a caption when the directive has a label', async () => {
    const el = document.createElement('input');
    document.body.appendChild(el);

    await render(
      [{ type: 'point', ref: '@e1', label: 'Type your key here' }],
      makeResolver({ '@e1': el }),
    );
    expect(document.body.textContent).toContain('Type your key here');
  });

  it('focuses the element when the directive asks for focus', async () => {
    const el = document.createElement('input');
    document.body.appendChild(el);

    await render(
      [{ type: 'point', ref: '@e1', focus: true }],
      makeResolver({ '@e1': el }),
    );
    expect(document.activeElement).toBe(el);
  });

  it('does not focus when focus is not requested', async () => {
    const el = document.createElement('input');
    document.body.appendChild(el);

    await render(
      [{ type: 'point', ref: '@e1' }],
      makeResolver({ '@e1': el }),
    );
    expect(document.activeElement).not.toBe(el);
  });

  it('scrolls an off-screen target into view before drawing it', async () => {
    const el = document.createElement('button');
    document.body.appendChild(el);

    // Report the element below the viewport so it counts as off-screen.
    el.getBoundingClientRect = () =>
      ({ top: 5000, left: 0, bottom: 5040, right: 80, width: 80, height: 40, x: 0, y: 5000 }) as DOMRect;

    let scrolled = false;
    el.scrollIntoView = () => {
      scrolled = true;
    };

    await render(
      [{ type: 'point', ref: '@e1' }],
      makeResolver({ '@e1': el }),
    );

    // Let the visibility wait resolve and its rAF-scheduled re-measure
    // run, so the now-ready target is drawn.
    await act(async () => {
      await new Promise<void>((r) => requestAnimationFrame(() => r()));
    });

    // The off-screen target was scrolled into view, and once the
    // (stubbed) IntersectionObserver reports it visible the overlay
    // draws the spotlight.
    expect(scrolled).toBe(true);
    expect(
      document.querySelector('[data-chat-highlight-overlay]'),
    ).not.toBeNull();
  });
});
