import { describe, expect, it } from "vitest";

import { REST, recallNext, recallPrevious, type RecallLadder } from "./ladder";

/**
 * The ladder, walked. Pure state, so no DOM and no hook — the same split
 * `core/links` and `core/compose/queue` make.
 *
 * The property under nearly every case below is the same one: **the user's
 * draft must survive a walk.** A user presses Up once out of curiosity, and
 * their half-written message has to come back.
 */

const ladder = (sent: string[], queued: string[] = []): RecallLadder => ({ sent, queued });

/** Walk up `n` times from rest, returning the final move. */
function up(l: RecallLadder, draft: string, n: number) {
  let move = recallPrevious(REST, l, draft);
  for (let i = 1; i < n; i++) move = recallPrevious(move.state, l, draft);
  return move;
}

describe("recall ladder", () => {
  it("walks sent prompts newest first", () => {
    const l = ladder(["oldest", "middle", "newest"]);

    expect(up(l, "", 1).text).toBe("newest");
    expect(up(l, "", 2).text).toBe("middle");
    expect(up(l, "", 3).text).toBe("oldest");
  });

  /** Wrapping would make a long ladder an infinite loop with no end to feel. */
  it("stops at the oldest entry rather than wrapping", () => {
    const l = ladder(["oldest", "newest"]);
    const atTop = up(l, "", 2);

    const beyond = recallPrevious(atTop.state, l, "");
    expect(beyond.text).toBeNull();
    expect(beyond.state).toBe(atTop.state);
  });

  it("says nothing moved when there is no history", () => {
    expect(recallPrevious(REST, ladder([]), "typing").text).toBeNull();
  });

  /** The whole point: the draft comes back. */
  it("restores the stashed draft on the way down", () => {
    const l = ladder(["one", "two"]);
    const walked = up(l, "half-written", 2);
    expect(walked.text).toBe("one");

    const back = recallNext(walked.state, l);
    expect(back.text).toBe("two");
    const rest = recallNext(back.state, l);
    expect(rest.text).toBe("half-written");
    expect(rest.state).toEqual(REST);
  });

  /**
   * Stashing on EVERY step would overwrite the draft with a recalled entry, and
   * the user's text would be gone with no way back — silently, since the buffer
   * still holds plausible-looking text.
   */
  it("stashes the draft once, not on every step", () => {
    const l = ladder(["one", "two", "three"]);
    const walked = up(l, "mine", 3);

    expect(walked.state.stashedDraft).toBe("mine");
  });

  it("does nothing on ArrowDown at rest", () => {
    const move = recallNext(REST, ladder(["one"]));
    expect(move.text).toBeNull();
    expect(move.state).toBe(REST);
  });

  /**
   * A queued prompt is nearer in time than anything sent, so it is the first
   * rung above the draft.
   */
  it("puts the newest queued prompt directly above the draft", () => {
    const l = ladder(["sent-one"], ["queued-a", "queued-b"]);

    const first = recallPrevious(REST, l, "draft");
    expect(first.text).toBe("queued-b");

    const second = recallPrevious(first.state, l, "draft");
    expect(second.text).toBe("sent-one");
  });

  /**
   * The archive's own defect, ported as a test rather than as code: stepping back
   * UP off the pending rung must re-enter the sent entries, and the following
   * ArrowDown must walk back through them — not jump straight to the draft,
   * skipping everything just visited.
   */
  it("descends through sent entries after climbing past the queued rung", () => {
    const l = ladder(["older", "newer"], ["pending"]);

    const r1 = recallPrevious(REST, l, "draft"); // queued
    const r2 = recallPrevious(r1.state, l, "draft"); // newer
    const r3 = recallPrevious(r2.state, l, "draft"); // older
    expect([r1.text, r2.text, r3.text]).toEqual(["pending", "newer", "older"]);

    const d1 = recallNext(r3.state, l);
    const d2 = recallNext(d1.state, l);
    const d3 = recallNext(d2.state, l);
    const d4 = recallNext(d3.state, l);
    expect([d1.text, d2.text, d3.text, d4.text]).toEqual([
      "newer",
      "pending",
      "draft",
      null,
    ]);
  });

  /** An empty queued entry is not a rung — landing on it would blank the buffer. */
  it("skips a queued rung whose text is empty", () => {
    const l = ladder(["sent-one"], [""]);
    expect(recallPrevious(REST, l, "draft").text).toBe("sent-one");
  });

  /**
   * `lastRecalled` is what `bufferIsRecallOwned` reads. Left set after landing on
   * the draft, a restored draft would look recall-owned and the next arrow would
   * navigate away from text the user is holding.
   */
  it("clears lastRecalled when it lands back on the draft", () => {
    const l = ladder(["one"]);
    const walked = recallPrevious(REST, l, "mine");
    expect(walked.state.lastRecalled).toBe("one");

    expect(recallNext(walked.state, l).state.lastRecalled).toBeNull();
  });

  /** Every move is a new object: a mutated state would defeat React's memo. */
  it("never mutates the state it was given", () => {
    const l = ladder(["one", "two"]);
    const first = recallPrevious(REST, l, "draft");
    const snapshot = { ...first.state };

    recallPrevious(first.state, l, "draft");
    recallNext(first.state, l);

    expect(first.state).toEqual(snapshot);
  });
});
