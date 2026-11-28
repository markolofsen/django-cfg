import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

const SOURCE = readFileSync(join(import.meta.dirname, "use-autosize.ts"), "utf8");

/**
 * The wrap flag must not be measured at the width it itself sets.
 *
 * `data-multiline` widens the field, so asking a WIDE field "do you wrap?" asks
 * about a width the answer created: the text fits, the flag drops, the field
 * narrows, the text wraps, the flag returns. Measured at 19 flips over 36
 * keystrokes — one per character typed.
 *
 * jsdom lays nothing out, so `scrollHeight` is always 0 and a rendered test
 * cannot see this. The source is what carries the rule, so the source is what is
 * asserted: the measurement is pinned to the compact width.
 */
describe("the wrap decision is independent of its own effect", () => {
  it("measures at the compact width, not the current one", () => {
    // The READ is what matters — the declaration alone still compiles with the
    // probe disabled, which is the mutation this asserts against.
    expect(SOURCE).toContain("const compact = compactWidth.current");
    expect(SOURCE).toContain("node.style.width = `${compact}px`");
  });

  it("restores the width it borrowed for the probe", () => {
    // Measuring by assigning a width and leaving it there would freeze the
    // field at its compact size for good.
    expect(SOURCE).toContain("node.style.width = restore");
  });

  it("keeps the row count as the question, so the tolerance stays half a row", () => {
    expect(SOURCE).toContain("Math.round((node.scrollHeight - inset) / rowHeight)");
  });
});
