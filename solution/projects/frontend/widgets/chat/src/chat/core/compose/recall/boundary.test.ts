import { describe, expect, it } from "vitest";

import { atFirstLine, atLastLine, bufferIsRecallOwned } from "./boundary";

const caret = (start: number, end = start) => ({ start, end });

describe("atFirstLine", () => {
  it("is true in an empty composer", () => {
    expect(atFirstLine("", caret(0))).toBe(true);
  });

  /**
   * The rule that made ArrowUp usable. Requiring a wholly empty composer made it
   * a dead key in any multi-line draft; zsh asks whether the text LEFT OF THE
   * CARET holds a newline instead.
   */
  it("is true on the first line of a multi-line draft", () => {
    expect(atFirstLine("first\nsecond", caret(3))).toBe(true);
  });

  it("is false once a newline sits above the caret", () => {
    expect(atFirstLine("first\nsecond", caret(9))).toBe(false);
  });

  /** Up with text selected means extend-or-collapse; hijacking it destroys the selection. */
  it("is false while a selection is open, even on the first line", () => {
    expect(atFirstLine("first\nsecond", caret(1, 4))).toBe(false);
  });

  it("is false when the caret is unknown in a non-empty buffer", () => {
    expect(atFirstLine("text", null)).toBe(false);
  });
});

describe("atLastLine", () => {
  it("is true when nothing sits below the caret", () => {
    expect(atLastLine("first\nsecond", caret(12))).toBe(true);
  });

  it("is false with a newline below the caret", () => {
    expect(atLastLine("first\nsecond", caret(2))).toBe(false);
  });

  it("is false while a selection is open", () => {
    expect(atLastLine("one", caret(0, 3))).toBe(false);
  });
});

describe("bufferIsRecallOwned", () => {
  it("allows navigation from an empty buffer", () => {
    expect(bufferIsRecallOwned("", null)).toBe(true);
  });

  /** Text the user typed is theirs, and arrows only move the caret. */
  it("refuses navigation once the user has typed", () => {
    expect(bufferIsRecallOwned("my own words", null)).toBe(false);
  });

  it("allows navigation to continue through text recall itself wrote", () => {
    expect(bufferIsRecallOwned("summarise the thread", "summarise the thread")).toBe(true);
  });

  /** One character of editing hands the buffer back to the user. */
  it("refuses once a recalled entry has been edited", () => {
    expect(bufferIsRecallOwned("summarise the thread!", "summarise the thread")).toBe(false);
  });
});
