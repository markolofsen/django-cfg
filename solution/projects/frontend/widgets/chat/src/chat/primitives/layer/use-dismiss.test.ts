import { readFileSync } from "node:fs";
import { describe, expect, it, vi } from "vitest";

import { escapeDismisses, pressIsOutside } from "./use-dismiss";

/**
 * The dismissal rules.
 *
 * Split by rung on purpose. The two DECISIONS — is this press outside, does
 * this key dismiss — are pure and tested as functions. The two BINDINGS —
 * `pointerdown` rather than `click`, capture rather than bubble — have no
 * return value to assert without a DOM, and this workspace has no jsdom, so
 * they are held by a source ratchet instead. Neither rung can cover the other:
 * a regex cannot tell one ref from two, and a pure test cannot see which event
 * name was passed to `addEventListener`.
 */

const SOURCE = readFileSync(new URL("./use-dismiss.ts", import.meta.url), "utf8");

/** A node that answers `contains` for itself and its declared descendants. */
function node(...descendants: unknown[]) {
  const self = {
    contains: (other: unknown): boolean => other === self || descendants.includes(other),
  };
  return self;
}

describe("pressIsOutside", () => {
  it("treats a press on the panel as inside", () => {
    const row = {};
    const panel = node(row);
    expect(pressIsOutside(row, [{ current: panel }])).toBe(false);
  });

  it("treats a press on the TRIGGER as inside", () => {
    // MUTANT: pass only the panel ref → this dies.
    //
    // The defect it guards is specific and looks like nothing: with the trigger
    // counted as outside, pressing it dismisses (from this hook) and re-opens
    // (from its own onClick) in ONE gesture, so the panel can never be closed
    // by the button that opened it.
    const trigger = node();
    const panel = node();
    expect(pressIsOutside(trigger, [{ current: panel }, { current: trigger }])).toBe(false);
  });

  it("treats a press anywhere else as outside", () => {
    const panel = node();
    expect(pressIsOutside({}, [{ current: panel }])).toBe(true);
  });

  it("survives a ref that has not attached yet", () => {
    // A ref is null for the first render of an open surface. Reading `.contains`
    // off it would throw inside a document-level listener, which takes the whole
    // page's pointer handling down rather than just this menu.
    expect(pressIsOutside({}, [{ current: null }])).toBe(true);
  });
});

describe("escapeDismisses", () => {
  it("dismisses on Escape and stops the key there", () => {
    // MUTANT: drop the stopPropagation → this dies. Chat panes and dialogs also
    // close on Escape, so one press would take the surface behind the menu down
    // with it.
    const stopPropagation = vi.fn();
    expect(escapeDismisses({ key: "Escape", stopPropagation })).toBe(true);
    expect(stopPropagation).toHaveBeenCalledOnce();
  });

  it("ignores every other key, and does not swallow it", () => {
    const stopPropagation = vi.fn();
    expect(escapeDismisses({ key: "a", stopPropagation })).toBe(false);
    expect(stopPropagation).not.toHaveBeenCalled();
  });
});

describe("the bindings (source ratchet — no DOM in this workspace)", () => {
  it("reads real code (control)", () => {
    // Every assertion below would pass vacuously on "".
    expect(SOURCE.length).toBeGreaterThan(500);
  });

  it("listens for pointerdown, never click", () => {
    // A click fires after the press has moved focus and possibly unmounted what
    // was under the pointer, so the dismissal lands a frame late.
    expect(SOURCE).toContain('addEventListener("pointerdown"');
    expect(SOURCE).not.toContain('addEventListener("click"');
  });

  it("binds in the capture phase, both ways", () => {
    // A row inside the surface may stopPropagation for its own reasons.
    // Registering in the bubble phase makes dismissal depend on every other
    // handler being polite.
    expect(SOURCE).toMatch(/addEventListener\("pointerdown", onPointerDown, true\)/);
    expect(SOURCE).toMatch(/addEventListener\("keydown", onKeyDown, true\)/);
    expect(SOURCE).toMatch(/removeEventListener\("pointerdown", onPointerDown, true\)/);
    expect(SOURCE).toMatch(/removeEventListener\("keydown", onKeyDown, true\)/);
  });

  it("binds nothing while closed", () => {
    expect(SOURCE).toMatch(/if\s*\(!open\)\s*return undefined/);
  });
});
