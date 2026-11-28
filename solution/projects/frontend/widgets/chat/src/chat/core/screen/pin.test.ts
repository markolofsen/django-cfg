import { describe, expect, it } from "vitest";

import { PIN_THRESHOLD, distanceFromBottom, nextPinned } from "./pin";

const at = (scrollTop: number, clientHeight = 500, scrollHeight = 2000) => ({ scrollHeight, scrollTop, clientHeight });
const BOTTOM = 1500;

describe("distanceFromBottom", () => {
  it("is zero at the end and never negative (overscroll)", () => {
    expect(distanceFromBottom(at(BOTTOM))).toBe(0);
    expect(distanceFromBottom(at(BOTTOM + 30))).toBe(0);
  });
  it("counts the hidden part below", () => {
    expect(distanceFromBottom(at(1000))).toBe(500);
  });
});

describe("nextPinned", () => {
  it("at the bottom: pinned", () => {
    expect(nextPinned(false, at(BOTTOM), false)).toBe(true);
  });

  it("within the threshold: still pinned (a half-visible last line)", () => {
    expect(nextPinned(true, at(BOTTOM - PIN_THRESHOLD), false)).toBe(true);
  });

  it("past the threshold: the reader scrolled up on purpose, not pinned", () => {
    expect(nextPinned(true, at(BOTTOM - PIN_THRESHOLD - 1), false)).toBe(false);
  });

  it("scrolling back down re-pins", () => {
    expect(nextPinned(false, at(BOTTOM - 10), false)).toBe(true);
  });

  it("while settling, the browser's scroll is not the reader's: pinned stays pinned", () => {
    // Focus scrolling moved the scroller up 300px; a pinned reader is still pinned.
    expect(nextPinned(true, at(1200), true)).toBe(true);
  });

  it("while settling, a reader who had scrolled up stays unpinned even if the clamp lands at the bottom", () => {
    expect(nextPinned(false, at(BOTTOM), true)).toBe(false);
  });

  it("honours a custom threshold", () => {
    expect(nextPinned(true, at(BOTTOM - 150), false, 200)).toBe(true);
    expect(nextPinned(true, at(BOTTOM - 150), false, 100)).toBe(false);
  });
});
