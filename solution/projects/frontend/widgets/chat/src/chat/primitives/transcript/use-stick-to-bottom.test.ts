import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The transcript must follow content that grows AFTER mount.
 *
 * A source ratchet, because this file is now a thin adapter: the mechanism
 * lives in `use-stick-to-bottom`, and what can still break here is the WIRING —
 * which element is handed to which ref, and whether the follow is animated.
 *
 * The two defects it guards were both reported and reproduced in the browser.
 * A pinned transcript stopped following the moment a turn was sent, leaving the
 * reply off-screen; and a hard fling onto the bottom edge shook the text,
 * measured at 5–12 direction reversals with an 8–23px swing.
 */

const SOURCE = readFileSync(new URL("./use-stick-to-bottom.ts", import.meta.url), "utf8");
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

describe("the ratchet reads real code (control)", () => {
  it("has content after stripping comments", () => {
    expect(CODE.length).toBeGreaterThan(800);
    // And the stripper removed something — otherwise the prose above the code
    // would satisfy every assertion below.
    expect(CODE.length).toBeLessThan(SOURCE.length * 0.7);
  });
});

describe("the mechanism is delegated, not reimplemented", () => {
  it("uses the library rather than writing scrollTop by hand", () => {
    // MUTANT: go back to an instant `node.scrollTop = ...`. That is what shook
    // on a fling — the write, the engine's own settle and the scroll event it
    // raises all land inside one frame and chase each other. Two attempts to
    // tune it out (a tolerance around the target, rounding the box's fractional
    // height) both failed, and a write-trap proved the hook was not even the
    // one writing during the shake.
    expect(CODE).toMatch(/from "use-stick-to-bottom"/);
    expect(CODE).not.toMatch(/\.scrollTop\s*=/);
  });

  it("animates growth but not arrival", () => {
    // MUTANT: `resize: "instant"` → the shake returns, because an instant land
    // has no frame between "not there" and "there" for a correction to blend
    // into. This is the whole reason for the swap.
    expect(CODE).toMatch(/resize:\s*"smooth"/);
    // MUTANT: `initial: "smooth"` → every room switch animates a scroll the
    // reader never started. There is nothing on screen to follow yet, so the
    // motion is pure noise; the bottom is just where a room opens.
    expect(CODE).toMatch(/initial:\s*"instant"/);
  });
});

describe("two elements, and they are not interchangeable", () => {
  it("hands the scroller and the content to different refs", () => {
    // MUTANT: pass the same node to both → the library measures the viewport
    // instead of the content, so growth is invisible and the follow never
    // fires. The scroller's height is the pane's; only the content's height
    // changes when a reply streams.
    expect(CODE).toMatch(/scrollRef\(node\)/);
    expect(CODE).toMatch(/contentRef\(node\)/);
    expect(CODE).toMatch(/contentRef:\s*content/);
  });

  it("reports the pin from the library's own state", () => {
    // MUTANT: hardcode `isPinned: true` → the jump-to-latest control never
    // appears, and a reader scrolled into history has no way back.
    expect(CODE).toMatch(/isPinned:\s*isAtBottom/);
  });
});
