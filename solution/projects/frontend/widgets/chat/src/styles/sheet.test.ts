import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * The page must never show through the sheet. On iOS Chrome the autofill bar above the keyboard is not part of
 * `visualViewport.height`, so a strip the sheet does not cover appears between it and the keyboard. The backing has to
 * paint OUTSIDE the sheet's box: a fixed `::before` is clipped by the sheet's own `overflow: hidden` once the dialog's
 * transform makes the sheet its containing block, a `box-shadow` is not. CSS cannot be rendered in vitest, so the rule is pinned as text.
 */
const css = readFileSync(join(import.meta.dirname, "sheet.css"), "utf8");

describe("chat sheet backing", () => {
  it("paints the backing with a box-shadow that outgrows the viewport", () => {
    expect(css).toMatch(/\.chat-sheet\s*\{\s*box-shadow:\s*0 0 0 100vmax var\(--background/);
  });

  it("does not rely on a clipped pseudo-element", () => {
    expect(css).not.toMatch(/\.chat-sheet::before/);
  });
});
