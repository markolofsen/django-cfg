import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * A source ratchet over the effects, because the rules alone prove nothing.
 *
 * `core/compose/draft-storage.ts` is fully unit-tested, and every one of those tests
 * would still pass if this hook never called a single one of them — the same
 * shape as the voice state machine that shipped with no consumer. The claims
 * here are about which store is used, what is persisted, and that the gate is
 * consulted, none of which a pure test can see and none of which this
 * workspace can assert in a DOM.
 */

const SOURCE = readFileSync(new URL("./use-draft-persistence.ts", import.meta.url), "utf8");
/** Comments state the rules too; stripping them stops a doc line satisfying a test. */
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

describe("the ratchet reads real code (control)", () => {
  it("has content after stripping comments", () => {
    expect(CODE.length).toBeGreaterThan(800);
    expect(CODE.length).toBeLessThan(SOURCE.length * 0.6);
  });
});

describe("the store choice", () => {
  it("uses sessionStorage, never localStorage", () => {
    // MUTANT: swap to localStorage → this dies. An unsent draft outliving the
    // session is the failure this choice exists to prevent: yesterday's
    // half-sentence reappearing in a room the user has moved on from.
    expect(CODE).toContain("sessionStorage");
    expect(CODE).not.toContain("localStorage");
  });

  it("guards every storage access", () => {
    // A sandboxed iframe THROWS on property access rather than returning null,
    // so an unguarded read takes the whole composer down with it.
    expect(CODE.match(/try\s*\{/g) ?? []).toHaveLength(2);
  });
});

describe("what is persisted", () => {
  it("saves the TEXT and nothing else", () => {
    // MUTANT: persist `draft` → this dies. A staged file is an object-URL
    // pinned to this document; restored, it is a chip that renders and cannot
    // send — work lost while looking intact.
    // `[\s\S]*?` rather than `[^)]*`: the key argument is itself a CALL, so a
    // no-paren class stops at `draftStorageKey(` and never reaches the text.
    expect(CODE).toMatch(/write\([\s\S]*?draft\.text\)/);
    expect(CODE).not.toMatch(/JSON\.stringify/);
  });

  it("delegates both decisions rather than re-deciding them here", () => {
    // Two spellings of one rule drift the first time only one is changed.
    expect(CODE).toContain("draftWrite(");
    expect(CODE).toContain("restoredDraft(");
  });
});

describe("the ordering that protects a stored draft", () => {
  it("consults the gate before writing", () => {
    // MUTANT: delete the guard → this dies, and the loss is silent: the save
    // effect fires with the empty pre-restore text and removes the entry it was
    // about to restore.
    expect(CODE).toContain("mayPersist(restored.current, room)");
    const gate = CODE.indexOf("mayPersist(");
    const save = CODE.lastIndexOf("write(draftStorageKey(room), draft.text)");
    expect(gate).toBeGreaterThan(-1);
    expect(save).toBeGreaterThan(gate);
  });

  it("marks the room restored even when nothing was stored", () => {
    // MUTANT: move the assignment inside the `if` → this dies, and a room with
    // no stored draft would never save one either: the gate stays shut forever.
    expect(CODE).toMatch(/restored\.current = room;[\s\S]{0,120}?if \(stored !== null\)/);
  });

  it("re-runs the restore when the room changes", () => {
    // Keyed on `room`, not `[]`: switching conversations must load that room's
    // draft, not keep the previous one in the field.
    expect(CODE).toMatch(/\}, \[room\]\)/);
  });
});
