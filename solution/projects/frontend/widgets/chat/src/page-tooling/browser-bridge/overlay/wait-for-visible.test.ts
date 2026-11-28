// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";

import { waitForVisible } from "./wait-for-visible";

const ORIGINAL_OBSERVER = globalThis.IntersectionObserver;

/** Place an element at a known rect; jsdom lays nothing out on its own. */
function elementAt(rect: Partial<DOMRect>): HTMLElement {
  const el = document.createElement("div");
  el.getBoundingClientRect = () =>
    ({
      width: 100,
      height: 100,
      top: 0,
      left: 0,
      right: 100,
      bottom: 100,
      x: 0,
      y: 0,
      ...rect,
      toJSON: () => ({}),
    }) as DOMRect;
  document.body.appendChild(el);
  return el;
}

/** An observer that accepts `observe()` and never calls back. */
function silentObserver() {
  globalThis.IntersectionObserver = class {
    observe() {}
    disconnect() {}
    unobserve() {}
    takeRecords() {
      return [];
    }
    root = null;
    rootMargin = "";
    thresholds = [];
  } as never;
}

afterEach(() => {
  globalThis.IntersectionObserver = ORIGINAL_OBSERVER;
  document.body.replaceChildren();
  vi.useRealTimers();
});

describe("waitForVisible", () => {
  /**
   * The case that failed in a real browser: an embedded, unpainted frame
   * delivers NO observer callback at all — not even a non-intersecting one.
   * Treating silence as "hidden" fails an approved action on an element that
   * is plainly on screen.
   */
  it("measures geometry when the observer never fires", async () => {
    silentObserver();
    const el = elementAt({ top: 100, bottom: 200 });

    await expect(waitForVisible(el, { timeoutMs: 10 })).resolves.toBe(true);
  });

  it("still reports an off-screen element as not visible", async () => {
    silentObserver();
    const el = elementAt({ top: 5000, bottom: 5100 });

    await expect(waitForVisible(el, { timeoutMs: 10 })).resolves.toBe(false);
  });

  it("reports a zero-sized element as not visible", async () => {
    silentObserver();
    const el = elementAt({ width: 0, height: 0, right: 0, bottom: 0 });

    await expect(waitForVisible(el, { timeoutMs: 10 })).resolves.toBe(false);
  });

  it("measures when there is no IntersectionObserver at all", async () => {
    // @ts-expect-error — deleting a global for the no-support path.
    delete globalThis.IntersectionObserver;
    const el = elementAt({ top: 10, bottom: 110 });

    await expect(waitForVisible(el, { timeoutMs: 10 })).resolves.toBe(true);
  });

  it("resolves true as soon as the observer reports an intersection", async () => {
    globalThis.IntersectionObserver = class {
      constructor(private readonly cb: IntersectionObserverCallback) {}
      observe(target: Element) {
        this.cb([{ isIntersecting: true, intersectionRatio: 1, target } as never], this as never);
      }
      disconnect() {}
      unobserve() {}
      takeRecords() {
        return [];
      }
      root = null;
      rootMargin = "";
      thresholds = [];
    } as never;
    // Off-screen by geometry: proves the TRUE came from the observer, not the
    // fallback measurement.
    const el = elementAt({ top: 9000, bottom: 9100 });

    await expect(waitForVisible(el, { timeoutMs: 10 })).resolves.toBe(true);
  });
});
