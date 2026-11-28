import { describe, expect, it } from "vitest";

import { DOCK_HEIGHT } from "./player-dock";

/**
 * The one geometry value this component owns, and why its SHAPE is checked.
 *
 * Tailwind's scanner is TEXTUAL: a class name assembled by concatenation, or
 * read from a variable that never appears as a literal, is never generated — and
 * the utility is then silently absent. That is not theoretical. `bottom-8`
 * written as a bare scale step in this file computed to `-56px` in the browser
 * and put the entire dock below the viewport, while every test in this package
 * stayed green and every story passed.
 *
 * Everything else about the frame's position is anchored to this row's own edges
 * (`bottom-full`), so there is no second number to keep in step.
 */
describe("dock geometry", () => {
  it("keeps the row height a literal arbitrary value Tailwind can scan", () => {
    // MUTANT: rewrite as a scale step (`h-14`) or build it by interpolation →
    // this fails. Both are the shapes that produced a missing utility.
    expect(DOCK_HEIGHT).toMatch(/^h-\[[\d.]+rem\]$/);
  });
});
