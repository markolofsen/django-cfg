import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The recipient list is a popover over the page, not a block in the box: opening it must not move the field.
 * A source ratchet (no jsdom here); the browser check is the real gate.
 */
const SOURCE = readFileSync(new URL("./recipient-chip.tsx", import.meta.url), "utf8");
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

describe("recipient chip menu", () => {
  it("is a portalled ui-core dropdown that opens upward", () => {
    expect(CODE).toMatch(/DropdownMenuContent/);
    expect(CODE).toMatch(/side="top"/);
  });
  it("keeps no inline open state", () => {
    expect(CODE).not.toMatch(/useState|role="radiogroup"/);
  });
  it("is a radio group whose rows are 44px targets, with a lock for private ones", () => {
    expect(CODE).toMatch(/DropdownMenuRadioGroup/);
    expect(CODE).toMatch(/min-h-11/);
    expect(CODE).toMatch(/locked \? Lock : Users/);
  });
  it("returns focus to the field, not the chip", () => {
    expect(CODE).toMatch(/onCloseAutoFocus[\s\S]*preventDefault[\s\S]*focusComposerField/);
  });
});
