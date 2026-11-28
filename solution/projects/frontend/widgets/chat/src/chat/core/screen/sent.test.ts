import { describe, expect, it } from "vitest";

import { isOwnSend, type SentRole } from "./sent";

/**
 * The reported defect: a reader scrolled into history sent a message and the
 * view stayed where it was, so their own text landed off-screen and the room
 * looked as if nothing had happened.
 *
 * Every case below is a way the naive fix — "the tail is a user message" — is
 * wrong, and each is silent in a rendered scroll position.
 */

const roles = (map: Record<string, SentRole>) => (id: string) => map[id];

const HISTORY = ["m1", "m2", "m3"];
const ROLES = roles({ m1: "user", m2: "assistant", m3: "user", m4: "user", m5: "assistant" });

describe("isOwnSend", () => {
  it("is true when the reader's own message is appended", () => {
    expect(isOwnSend(HISTORY, [...HISTORY, "m4"], ROLES)).toBe(true);
  });

  it("is false for the assistant opening its reply", () => {
    // MUTANT: drop the role check → this passes, and every token of every reply
    // drags a reader out of the history they scrolled up to read.
    expect(isOwnSend(HISTORY, [...HISTORY, "m5"], ROLES)).toBe(false);
  });

  it("is false on the first observation", () => {
    // A room opens at the bottom already; scrolling there again animates a
    // motion the reader never started. `m3` is a user message, so this is
    // exactly the case a tail-only check gets wrong.
    expect(isOwnSend(null, HISTORY, ROLES)).toBe(false);
  });

  it("is false when the transcript was replaced wholesale", () => {
    // MUTANT: compare only the tail → a room whose history ends on a user
    // message scrolls on every switch into it. The store outlives the switch,
    // so this is not hypothetical.
    expect(isOwnSend(HISTORY, ["x1", "x2", "x3", "m4"], ROLES)).toBe(false);
  });

  it("is false when history pages in above", () => {
    // The list grew, and the tail is still the same user message — but the
    // reader asked for those rows where they are, not at the bottom.
    expect(isOwnSend(["m3"], ["m1", "m2", "m3"], ROLES)).toBe(false);
  });

  it("is false when more than one row arrives at once", () => {
    expect(isOwnSend(HISTORY, [...HISTORY, "m5", "m4"], ROLES)).toBe(false);
  });

  it("is false when nothing changed", () => {
    expect(isOwnSend(HISTORY, HISTORY, ROLES)).toBe(false);
  });

  it("is false for an id the store has no message for", () => {
    // Dropped rather than guessed: defaulting to `user` would scroll on a
    // phantom row, which is the failure `missedRows` documents from the other
    // side of the same invariant.
    expect(isOwnSend(HISTORY, [...HISTORY, "ghost"], ROLES)).toBe(false);
  });
});
