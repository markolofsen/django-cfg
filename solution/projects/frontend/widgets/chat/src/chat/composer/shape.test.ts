import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The composer's SHAPE: one row until the draft earns a second, and a box that
 * is clickable over its whole area.
 *
 * A source ratchet, because both claims are about layout and binding rather
 * than about a return value, and this workspace has no jsdom. The rung is
 * chosen, not settled for. The browser measurement in the owning plan is what
 * proves the shape renders; these assertions are what stop it silently
 * reverting to the grid that made an EMPTY composer two rows tall.
 */

const read = (name: string) =>
  readFileSync(new URL(name, import.meta.url), "utf8");

const COMPOSER = read("./composer.tsx");
// The caret rule moved here when the tool menu became its second caller: two
// controls need it and neither owns the textarea.
const FOCUS = read("./focus-field.ts");
// Autosize moved to its own file; the assertions follow the CODE, not the
// filename it used to live in.
const INPUT = read("./field/use-autosize.ts");
// The CSS half of the cap is declared on the element, which stayed behind.
const FIELD = read("./field/input.tsx");

describe("the ratchet reads real code (control)", () => {
  it("both files have content", () => {
    expect(COMPOSER.length).toBeGreaterThan(1000);
    expect(INPUT.length).toBeGreaterThan(1000);
  });
});

describe("autosize prefers the browser's own", () => {
  it("detects field-sizing ONCE, at module scope", () => {
    // MUTANT: move the check inside `resize` → this dies. It is a property of
    // the engine and cannot change while the page is loaded; asking per
    // keystroke is work that can only return the same answer.
    expect(INPUT).toMatch(/^export const FIELD_SIZING =/m);
    expect(INPUT).toContain('CSS.supports("field-sizing", "content")');
  });

  it("keeps the measured fallback for browsers without it", () => {
    // Firefox has no support and Safari gained it only at 26. Deleting the
    // effect would leave those browsers with a one-row box that never grows.
    expect(INPUT).toContain("node.scrollHeight");
    expect(INPUT).toMatch(/useLayoutEffect\(resize/);
  });

  it("never runs both — a written height would override the CSS", () => {
    // MUTANT: drop the early return → this dies. The effect writes
    // `style.height`, which beats `field-sizing` and re-introduces the
    // measure-and-write cycle the CSS exists to remove.
    expect(INPUT).toMatch(/if \(FIELD_SIZING\) return;/);
  });

  it("caps at maxRows in BOTH paths, from the one number", () => {
    // Two caps that can drift apart is how a host ends up styling one and
    // getting the other. `lh` is the row unit, so the CSS cap follows whatever
    // line-height the host set.
    expect(FIELD).toContain("`${maxRows}lh`");
    expect(INPUT).toMatch(/lineHeight \* maxRows/);
  });
});

describe("the whole box is clickable", () => {
  it("focuses the field on a press, caret at the END", () => {
    // End, never start: a click into the padding beneath a written draft means
    // "let me keep typing", not "let me edit the beginning".
    expect(FOCUS).toContain("field.setSelectionRange(end, end)");
    expect(FOCUS).toContain("field.value.length");
  });

  it("ignores a press that landed on a control", () => {
    // MUTANT: delete the target check → this dies. Without it, clicking the mic
    // or a chip ALSO focuses the textarea and steals the press from the control
    // the user actually aimed at.
    expect(COMPOSER).toMatch(/event\.target !== event\.currentTarget/);
  });

  it("returns the caret to the field after a tool is picked", () => {
    // MUTANT: drop the call in `onPick` → this dies. A pick states an intent
    // and the sentence naming its object comes next; a dialog that closes with
    // focus nowhere loses that keystroke. Asserted on the source because the
    // workspace has no jsdom — the behaviour itself is held by the story
    // `PickStagesAChip`.
    expect(read("./controls/tools.tsx")).toMatch(/focusComposerField\(/);
  });

  it("leaves an already-focused field's caret alone", () => {
    // Re-running setSelectionRange on the active field would fight a real caret
    // placement — clicking mid-text would jump the caret to the end.
    expect(FOCUS).toMatch(/field === document\.activeElement/);
  });

  it("is a form press, not a <label> wrapper", () => {
    // A label click also ACTIVATES its control, and this wrapper holds buttons
    // whose activation would then double-fire.
    expect(COMPOSER).not.toMatch(/<label/);
    expect(COMPOSER).toContain("onPointerDown={onPointerDown}");
  });
});
