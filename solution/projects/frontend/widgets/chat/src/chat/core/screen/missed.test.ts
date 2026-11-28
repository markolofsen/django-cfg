import { describe, expect, it } from "vitest";

import { MissedCount, missedRows, type MissedRole } from "./missed";

const row = (id: string, role: MissedRole = "assistant") => ({ id, role });

describe("counting what arrived while scrolled away", () => {
  it("counts nothing while the reader is at the bottom", () => {
    const missed = new MissedCount();
    missed.observe(true, [row("a"), row("b")]);
    expect(missed.value()).toBeNull();
  });

  it("counts replies that arrive after the reader leaves", () => {
    const missed = new MissedCount();
    missed.observe(false, [row("a"), row("b")]);
    missed.observe(false, [row("a"), row("b"), row("c")]);
    expect(missed.value()).toBe(1);
  });

  /**
   * The baseline is what was on screen when the reader left, NOT a length. A
   * history load prepends rows the reader has not fallen behind on; counting by
   * length would report them as a wall of new replies.
   */
  it("does not count older messages loaded above", () => {
    const missed = new MissedCount();
    missed.observe(false, [row("c"), row("d")]);
    missed.observe(false, [row("a"), row("b"), row("c"), row("d")]);
    expect(missed.value()).toBeNull();
  });

  /**
   * A badge saying "1 new" that points at your own sentence is worse than none.
   * Mirrors the server's unread rule, which excludes human rows.
   */
  it("never counts the reader's own messages", () => {
    const missed = new MissedCount();
    missed.observe(false, [row("a")]);
    missed.observe(false, [row("a"), row("mine", "user")]);
    expect(missed.value()).toBeNull();
  });

  it("counts a system row — a failed turn is news", () => {
    const missed = new MissedCount();
    missed.observe(false, [row("a")]);
    missed.observe(false, [row("a"), row("failed", "system")]);
    expect(missed.value()).toBe(1);
  });

  it("clears when the reader returns to the bottom", () => {
    const missed = new MissedCount();
    missed.observe(false, [row("a")]);
    missed.observe(false, [row("a"), row("b")]);
    expect(missed.value()).toBe(1);
    missed.observe(true, [row("a"), row("b")]);
    expect(missed.value()).toBeNull();
  });

  /**
   * Leaving again starts a NEW baseline. Without the reset on re-pin the second
   * departure would still be counting against the first one's snapshot and
   * report everything since as unread.
   */
  it("starts over after returning and leaving again", () => {
    const missed = new MissedCount();
    missed.observe(false, [row("a")]);
    missed.observe(false, [row("a"), row("b")]);
    missed.observe(true, [row("a"), row("b")]);
    missed.observe(false, [row("a"), row("b")]);
    expect(missed.value()).toBeNull();
  });

  /**
   * A frontier can disappear — a cleared transcript, a switched room. Searching
   * for it then yields -1, and slicing from there would count every row as new.
   */
  it("re-arms rather than counting everything when the frontier vanishes", () => {
    const missed = new MissedCount();
    missed.observe(false, [row("a"), row("b")]);
    missed.observe(false, [row("x"), row("y"), row("z")]);
    expect(missed.value()).toBeNull();
  });

  /** Unpinned on an empty list: everything that arrives after is genuinely new. */
  it("counts from nothing when the transcript was empty", () => {
    const missed = new MissedCount();
    missed.observe(false, []);
    missed.observe(false, [row("a"), row("b")]);
    expect(missed.value()).toBe(2);
  });

  /**
   * Null, never 0: "the button is showing but nothing arrived" and "one arrived"
   * are different states, and only the second deserves a number.
   */
  it("reports null rather than zero when nothing arrived", () => {
    const missed = new MissedCount();
    missed.observe(false, [row("a"), row("b")]);
    expect(missed.value()).toBeNull();
  });
});

/**
 * The seam between the store and the counter.
 *
 * Every test above hands `MissedCount` rows that are already correct, so none
 * of them can see how those rows get BUILT — and that projection is where the
 * one judgement call lives. It used to default a missing message to
 * `assistant`, silently making an unknown row count as a reply.
 */
describe("projecting the transcript onto rows to count", () => {
  const byId = {
    a: { role: "user" as MissedRole },
    b: { role: "assistant" as MissedRole },
  };

  it("pairs each id with the role the store holds (control)", () => {
    // Without this, the drop test below would pass on an empty result and
    // prove nothing.
    expect(missedRows(["a", "b"], byId)).toEqual([
      { id: "a", role: "user" },
      { id: "b", role: "assistant" },
    ]);
  });

  it("keeps the transcript's order, not the map's", () => {
    expect(missedRows(["b", "a"], byId).map((r) => r.id)).toEqual(["b", "a"]);
  });

  it("drops an id the store has no message for", () => {
    // MUTANT: default the role instead of dropping → this dies.
    expect(missedRows(["a", "ghost", "b"], byId).map((r) => r.id)).toEqual(["a", "b"]);
  });

  it("does not let a dropped id become a counted reply", () => {
    // The consequence, stated as the badge shows it. A phantom row defaulted to
    // `assistant` reads as one new answer and sends the reader to a message
    // that does not exist. Counting through the real class rather than
    // asserting on the projection, because that is the path the badge takes.
    const missed = new MissedCount();
    missed.observe(false, missedRows(["a"], byId));
    missed.observe(false, missedRows(["a", "ghost"], byId));
    expect(missed.value()).toBeNull();
  });
});
