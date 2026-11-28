import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * Wide content scrolls inside its own box rather than widening the column.
 *
 * The transcript column is bounded by `min-w-0`, and prose is held by
 * `break-words` — but neither reaches INSIDE a block element. A table or a
 * fenced block lays out at its content width regardless, so each one has to
 * carry its own guard. Without it the column grows to fit and the whole
 * transcript scrolls sideways.
 *
 * Nothing else enforces this. The rule lives in CSS, no test read this
 * stylesheet, and the parts are supplied by an open registry — so "every
 * renderer boxes itself" was an unwritten convention, and `pre` had already
 * fallen out of it while the other four held.
 *
 * `break-words` is scoped to `group-[.is-user]`, which is the reason the gap
 * showed on code specifically: code arrives from the model, on the side that
 * has no word-breaking at all.
 */

/**
 * Every sheet the entry point pulls in, concatenated.
 *
 * Read from the `@import` list rather than named here: `styles/index.css` is an
 * entry point and the rules live beside it, so a hardcoded filename would go
 * stale the next time one is split out — silently, since a missing file reads
 * the same as a missing rule.
 */
// Paths inside the entry are relative to IT, not to this test.
const STYLES = import.meta.dirname;
const ENTRY = readFileSync(join(STYLES, "index.css"), "utf8");
const CSS = [...ENTRY.matchAll(/@import "\.\/([^"]+)"/g)]
  .map(([, path]) => readFileSync(join(STYLES, path ?? ""), "utf8"))
  .join("\n");

/** The declaration block for a selector, as authored. */
function ruleFor(selector: string): string {
  const at = CSS.indexOf(selector);
  if (at < 0) return "";
  return CSS.slice(at, CSS.indexOf("}", at));
}

describe("wide content scrolls instead of widening the column", () => {
  it("reads the stylesheets (control)", () => {
    // Every assertion below is a substring search, and "" satisfies none of
    // them — but an EMPTY import list would also produce "", so the count is
    // asserted first. A split that dropped a sheet must fail here rather than
    // let the rest pass over nothing.
    expect(CSS.length).toBeGreaterThan(2000);
    expect(CSS).toContain(".chat-surface");
  });

  it("boxes a fenced block", () => {
    // MUTANT: drop `overflow-x` from `:where(pre)` → this dies. That is the
    // state the file was in: font size, radius and line height, no guard.
    //
    // Measured live rather than reasoned: one 400-character line inside an
    // assistant turn took the transcript's scroller from 1218 to 3434 with
    // `overflow-x: visible`, and to exactly `clientWidth` with `auto`. No
    // element widened in either case — the `pre`, the content column and the
    // row all measured 768 throughout. The spill is the block's CONTENT
    // painting past an edge that never moved, which is why no width assertion
    // anywhere could have caught this.
    const pre = ruleFor(".chat-surface :where(pre)");
    expect(pre).toContain("overflow-x: auto");
  });

  it("boxes a table, the case this was modelled on", () => {
    const table = ruleFor(".chat-surface :where(table)");
    expect(table).toContain("overflow-x: auto");
    // `display: block` is what makes a table shrinkable at all; a real
    // `display: table` ignores the overflow and sizes to its widest row.
    expect(table).toContain("display: block");
  });

  it("boxes a diagram's fallback source, the one place text is shown verbatim", () => {
    // The listing a diagram degrades to when it cannot be drawn. It is the
    // agent's own source, so it keeps its lines: `pre`, not `pre-wrap`, because
    // a wrapped line reads as two lines of a language that has none.
    const literal = ruleFor(".chat-diagram-source");
    expect(literal).toContain("overflow-x: auto");
    expect(literal).toContain("white-space: pre");
  });

  it("boxes a rendered diagram, which sizes to its graph and not to the column", () => {
    const diagram = ruleFor(".chat-surface .chat-diagram {");
    expect(diagram).toContain("overflow-x: auto");
  });
});
