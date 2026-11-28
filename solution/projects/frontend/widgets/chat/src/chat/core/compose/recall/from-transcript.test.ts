import { describe, expect, it } from "vitest";

import { ladderFromMessages } from "./from-transcript";

/**
 * The ladder is what ArrowUp walks. Every rule here exists because the
 * alternative is visible: a step that yields nothing, a step that repeats
 * itself, or a step that pastes a file into the composer.
 */
describe("ladderFromMessages", () => {
  it("keeps only user turns, oldest first", () => {
    expect(
      ladderFromMessages([
        { role: "user", content: "first" },
        { role: "assistant", content: "an answer" },
        { role: "user", content: "second" },
        { role: "tool", content: "output" },
      ]),
    ).toEqual(["first", "second"]);
  });

  it("collapses an immediate repeat, so a double-send costs one step", () => {
    expect(
      ladderFromMessages([
        { role: "user", content: "retry" },
        { role: "user", content: "retry" },
        { role: "user", content: "moved on" },
      ]),
    ).toEqual(["retry", "moved on"]);
  });

  it("keeps a repeat that is not immediate — it was typed again deliberately", () => {
    expect(
      ladderFromMessages([
        { role: "user", content: "status" },
        { role: "user", content: "and now" },
        { role: "user", content: "status" },
      ]),
    ).toEqual(["status", "and now", "status"]);
  });

  it("trims, and drops a turn that is only whitespace", () => {
    expect(
      ladderFromMessages([
        { role: "user", content: "  padded  " },
        { role: "user", content: "   " },
      ]),
    ).toEqual(["padded"]);
  });

  it("drops an oversized entry rather than letting it evict the ladder", () => {
    const huge = "x".repeat(8_001);
    expect(
      ladderFromMessages([
        { role: "user", content: "keep me" },
        { role: "user", content: huge },
        { role: "user", content: "keep me too" },
      ]),
    ).toEqual(["keep me", "keep me too"]);
  });

  it("keeps the NEWEST entries when the room is longer than the limit", () => {
    const many = Array.from({ length: 60 }, (_, i) => ({
      role: "user",
      content: `p${i}`,
    }));
    const ladder = ladderFromMessages(many);
    expect(ladder).toHaveLength(50);
    // The oldest are what a person is least likely to reach for.
    expect(ladder[0]).toBe("p10");
    expect(ladder[49]).toBe("p59");
  });

  it("returns an empty ladder for a room with no user turns", () => {
    expect(ladderFromMessages([{ role: "assistant", content: "hello" }])).toEqual([]);
  });
});
