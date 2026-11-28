import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * Recall PREVIEWS; only Tab writes.
 *
 * This file exists because the change that introduced that rule was invisible
 * to the whole suite: `core/compose/recall` is tested exhaustively and was not touched,
 * so 581 tests stayed green while the hook's behaviour was rewritten underneath
 * them. The pure ladder answers "to what"; NOTHING covered "and then what
 * happens to the buffer", which is the part a user feels.
 *
 * A source ratchet, because the claims are about which key is claimed and what
 * is called in a keydown handler, and this workspace has no jsdom. The rung is
 * a deliberate floor, not a substitute for the browser check in the plan.
 */

const SOURCE = readFileSync(new URL("./use-recall.ts", import.meta.url), "utf8");
/** Comments state the rules too; stripping them stops a doc line satisfying a test. */
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

describe("the ratchet reads real code (control)", () => {
  it("has content after stripping comments", () => {
    expect(CODE.length).toBeGreaterThan(1500);
    // And the stripping actually removed something — otherwise a comment could
    // satisfy every assertion below.
    expect(CODE.length).toBeLessThan(SOURCE.length * 0.75);
  });
});

describe("walking never touches the buffer", () => {
  it("previews on an arrow instead of writing", () => {
    // MUTANT: `setText(move.text)` on the arrow path → this dies.
    //
    // The defect: a full-buffer rewrite per press reflows the composer, so the
    // line being read moves while it is read.
    expect(CODE).toMatch(/setPreview\(move\.state\.position\.kind === "draft" \? null : move\.text\)/);
  });

  it("calls setText exactly ONCE in the whole hook — on the Tab path", () => {
    // The strongest form of the rule: not "the arrow path doesn't write" but
    // "there is only one writer at all". A second call site is how this
    // regresses back to write-while-walking.
    expect(CODE.match(/setText\(/g) ?? []).toHaveLength(1);
  });

  it("ends the walk when the ladder lands back on the draft", () => {
    // The draft rung IS the user's own text. Previewing it would offer to
    // insert what is already in the box.
    expect(CODE).toContain('move.state.position.kind === "draft"');
  });
});

describe("Tab commits, and only while previewing", () => {
  it("inserts the previewed prompt with the caret at the end", () => {
    expect(CODE).toMatch(/if \(event\.key === "Tab"\)/);
    expect(CODE).toMatch(/setSelectionRange\(text\.length, text\.length\)/);
  });

  it("claims Tab ONLY inside the walking guard", () => {
    // MUTANT: hoist the Tab branch above the guard → this dies.
    //
    // An always-swallowed Tab makes the composer a keyboard trap with no way
    // out. That is an accessibility defect, not a preference, which is why the
    // guard is asserted structurally rather than by reading the branch.
    const guard = CODE.indexOf("walking.current !== null");
    const tab = CODE.indexOf('event.key === "Tab"');
    expect(guard).toBeGreaterThan(-1);
    expect(tab).toBeGreaterThan(guard);
  });

  it("reads the preview through a REF, not through state", () => {
    // A `useState` read inside the handler is one render stale, so the first
    // Tab after an arrow would fall through and move focus out of the composer.
    expect(CODE).toMatch(/walking\.current = preview/);
  });

  it("returns the ladder to rest on commit", () => {
    // Tolerant of other statements between them — the commit path also clears
    // the queued-entry ref — but the ORDER is the claim: rest, then drop the
    // preview, then write. Writing first would leave a live walk over a buffer
    // that no longer matches the rung it is standing on.
    expect(CODE).toMatch(/state\.current = REST;[\s\S]{0,200}?setPreview\(null\);[\s\S]{0,400}?setText\(text\)/);
  });
});

describe("Escape abandons with nothing to restore", () => {
  it("clears the preview and stops the key there", () => {
    // stopPropagation because the chat pane closes on Escape too: without it,
    // abandoning a walk would also close the surface behind the composer.
    expect(CODE).toMatch(/if \(event\.key === "Escape"\)/);
    expect(CODE).toContain("event.stopPropagation()");
  });

  it("has no restore step, because there was no write", () => {
    // MUTANT: reintroduce a stashed-draft restore → this dies. The draft was
    // never overwritten, so restoring it could only clobber later typing.
    expect(CODE).not.toMatch(/stashedDraft/);
  });
});

describe("typing abandons the walk", () => {
  it("drops the preview as soon as the draft has content", () => {
    // A preview hanging around while the user writes something new invites a
    // Tab that destroys it.
    expect(CODE).toMatch(/if \(preview !== null && draft\.text !== ""\)/);
  });

  it("clears the synchronous ref too, not only the state", () => {
    // MUTANT: drop the `walking.current = null` → this dies. State is one
    // render behind inside the handler, so a Tab in that window would still
    // find a preview and insert it over what the user just typed.
    expect(CODE).toMatch(/walking\.current = null/);
  });
});

describe("the owner's rule survives the redesign", () => {
  it("still refuses to navigate away from a non-empty draft", () => {
    expect(CODE).toContain("bufferIsRecallOwned(");
  });

  it("passes lastRecalled as null, since nothing is recall-owned any more", () => {
    // MUTANT: pass `state.current.lastRecalled` → this dies. With no writes the
    // buffer is ALWAYS the user's, and a remembered value could only weaken the
    // rule by making a real draft look recalled.
    expect(CODE).toMatch(/bufferIsRecallOwned\([^)]*, null\)/);
  });
});

/**
 * A queued prompt is TAKEN; a sent one is COPIED.
 *
 * The rung was inherited from the archive and the RULE was not. `use-recall.ts`
 * shipped with no call to `take` at all, so Tab inserted the text and left the
 * entry in the queue — the same prompt then sent twice, once as the edit and
 * once when the queue drained.
 */
describe("committing a queued rung removes it from the queue", () => {
  it("calls take on the Tab path", () => {
    // MUTANT: delete the `take(queuedId)` call → this dies, and the duplicate
    // send comes back with every other test still green.
    expect(CODE).toMatch(/if \(queuedId !== null\) take\(queuedId\)/);
  });

  it("remembers WHICH entry the preview came from", () => {
    // The text alone cannot tell a queued rung from a sent one: the same words
    // may sit on both. So the id is captured where the preview is written.
    expect(CODE).toMatch(/previewQueuedId/);
    expect(CODE).toMatch(/move\.state\.position\.kind === "queued"/);
  });

  it("reads the LAST queue entry, matching core/compose/recall's rung definition", () => {
    // The trap: if the two ever disagree, Tab takes a different prompt than the
    // one previewed — and both look correct in isolation.
    expect(CODE).toMatch(/queuedNow\[queuedNow\.length - 1\]/);
  });

  it("leaves the queue alone when the walk is abandoned", () => {
    // Escape and typing both end the walk without committing, so neither may
    // consume a queued prompt. Clearing the ref is what guarantees that: the
    // Tab path is the only reader, and it only acts on a non-null id.
    const clears = CODE.match(/previewQueuedId\.current = null/g) ?? [];
    expect(clears.length).toBeGreaterThanOrEqual(3);
  });
});

/**
 * The announcement follows both steps; it never performs one.
 *
 * This path removes THEN writes, while the queue's own edit path writes then
 * removes and drops the removal if the write was cancelled. That asymmetry is
 * deliberate. A listener asked to perform either step would invert one of the
 * two orders, and the failure is a prompt lost on cancel — silent, and visible
 * only to whoever typed it.
 */
describe("queue:taken is emitted, not acted on", () => {
  it("announces after the write, not before it", () => {
    // MUTANT: move the emit above `setText(text)` → this dies. The order is the
    // entire claim: an announcement made mid-sequence describes a state the
    // composer is not in yet.
    const write = CODE.indexOf("setText(text)");
    const emit = CODE.indexOf('events.emit("queue:taken"');
    expect(write).toBeGreaterThan(-1);
    expect(emit).toBeGreaterThan(write);
  });

  it("reads the entry through latest, not through the closure", () => {
    // The handler is memoized and does not re-create per keystroke, so a
    // closed-over `items` holds whatever the queue contained when it was built.
    // Every other queue read here already goes through the ref.
    expect(CODE).toMatch(/latest\.current\.items\.find/);
  });

  it("says nothing when the rung was a sent prompt", () => {
    // A sent prompt is COPIED and no queue entry moves, so there is nothing to
    // announce. The null guard is what keeps the event honest.
    expect(CODE).toMatch(/queuedId !== null && taken !== undefined/);
  });
});
