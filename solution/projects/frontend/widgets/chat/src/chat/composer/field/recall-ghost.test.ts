import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The recall ghost must be typed like the field, or Tab makes the text jump.
 *
 * A source ratchet (no jsdom here): the ghost takes the textarea's own `className` (font size, leading,
 * padding), stacks on its grid cell, wraps as a textarea does, and puts the TAB badge inline on the
 * text's baseline. The old overlay had `items-center`, its own `py-1`/`leading-6` and no font size.
 */
const SOURCE = readFileSync(new URL("./field.tsx", import.meta.url), "utf8");
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
const GHOST = CODE.slice(CODE.indexOf('role="status"'));

describe("recall ghost markup", () => {
  it("reads real code (control)", () => {
    expect(GHOST.length).toBeGreaterThan(200);
  });
  it("shares the textarea's typography through className", () => {
    expect(GHOST).toMatch(/\$\{className \?\? ""\}/);
  });
  it("has no private metrics of its own", () => {
    expect(GHOST).not.toMatch(/items-center|leading-6|\bpy-\d|\bgap-/);
  });
  it("sits in the textarea's grid cell and wraps like a textarea", () => {
    expect(CODE).toMatch(/col-start-1 row-start-1 \$\{className/);
    expect(GHOST).toMatch(/col-start-1 row-start-1/);
    expect(GHOST).toMatch(/whitespace-pre-wrap break-words/);
  });
  it("keeps the badge inline on the baseline and hides it on a narrow screen", () => {
    expect(GHOST).toMatch(/inline-block[^"]*align-baseline[^"]*max-sm:hidden/);
  });
});
