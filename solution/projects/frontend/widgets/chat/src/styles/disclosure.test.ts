import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

const CSS = readFileSync(join(import.meta.dirname, "block.css"), "utf8");

/**
 * The frame belongs to the OPEN state alone.
 *
 * Closed, a disclosure is one muted line among the turn's other chrome, and a
 * border there would box every collapsed reply. jsdom applies no stylesheet and
 * `details[open]` is not something a rendered test can assert on here, so the
 * source carries the rule and the source is what is pinned.
 */
describe("the reasoning frame", () => {
  it("is gated on [open], never on the bare class", () => {
    expect(CSS).toContain(".chat-disclosure[open] {");
    // MUTANT: an unqualified `.chat-disclosure { border: ... }` would frame a
    // collapsed line too. No border may be declared outside an [open] rule.
    const unqualified = /\.chat-disclosure\s*\{[^}]*border\s*:/;
    expect(unqualified.test(CSS)).toBe(false);
  });

  it("uses the host's tokens, not a pinned palette", () => {
    // A literal colour here would stop tracking the theme, which is exactly the
    // failure the package's style rules exist to prevent.
    expect(CSS).toContain("border: 1px solid var(--border)");
    expect(CSS).toContain("border-radius: var(--radius");
  });

  it("pulls the frame outward so the text keeps its column", () => {
    // Padding without the matching negative margin indents the summary relative
    // to the speaker line above and the reply below; all three share a left edge.
    expect(CSS).toContain("margin-inline: -0.625rem");
  });

  it("separates the frame from the reply beneath it", () => {
    expect(CSS).toContain("margin-block-end: 0.75rem");
  });
});
