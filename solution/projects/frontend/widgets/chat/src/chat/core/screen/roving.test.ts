import { describe, expect, it } from "vitest";

import { clampIndex, isRovingKey, nextIndex } from "./roving";

describe("which keys move within the transcript", () => {
  it("recognises the four", () => {
    for (const key of ["ArrowDown", "ArrowUp", "Home", "End"]) {
      expect(isRovingKey(key)).toBe(true);
    }
  });

  it("leaves everything else to the browser", () => {
    // The control. Claiming a key we do not handle would swallow it: PageDown
    // and Tab in particular are how a user leaves the transcript.
    for (const key of ["Tab", "PageDown", "Enter", " ", "a", "ArrowLeft"]) {
      expect(isRovingKey(key)).toBe(false);
    }
  });
});

describe("moving the active row", () => {
  it("steps down and up", () => {
    expect(nextIndex("ArrowDown", 0, 5)).toBe(1);
    expect(nextIndex("ArrowUp", 3, 5)).toBe(2);
  });

  it("jumps to the ends", () => {
    expect(nextIndex("Home", 3, 5)).toBe(0);
    expect(nextIndex("End", 1, 5)).toBe(4);
  });

  it("CLAMPS rather than wraps", () => {
    // Wrapping from the newest message back to the first is disorienting where
    // position carries meaning. Returning null (not the same index) is what lets
    // the caller skip preventDefault — see the next test.
    expect(nextIndex("ArrowDown", 4, 5)).toBeNull();
    expect(nextIndex("ArrowUp", 0, 5)).toBeNull();
  });

  it("reports 'nowhere' so the PAGE can still scroll at the last row", () => {
    // A user at the end of a transcript presses ArrowDown expecting the page to
    // move. Swallowing the key there — which is what returning `active` would
    // invite — takes that away and looks like a frozen page.
    expect(nextIndex("Home", 0, 5)).toBeNull();
    expect(nextIndex("End", 4, 5)).toBeNull();
  });

  it("moves nowhere in an empty transcript", () => {
    expect(nextIndex("ArrowDown", 0, 0)).toBeNull();
    expect(nextIndex("End", 0, 0)).toBeNull();
  });
});

describe("staying valid while the transcript grows", () => {
  it("keeps an index that is still in range", () => {
    expect(clampIndex(3, 5)).toBe(3);
  });

  it("pulls a stale index back into range when messages are removed", () => {
    // An index that outlives its row leaves EVERY row at tabIndex -1, so the
    // transcript stops being reachable by Tab and nothing looks broken.
    expect(clampIndex(9, 3)).toBe(2);
  });

  it("survives an empty transcript", () => {
    expect(clampIndex(4, 0)).toBe(0);
  });

  it("never returns a negative index", () => {
    expect(clampIndex(-1, 3)).toBe(0);
  });
});
