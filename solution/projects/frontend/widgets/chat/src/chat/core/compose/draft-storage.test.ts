import { describe, expect, it } from "vitest";

import {
  DRAFT_MAX_LENGTH,
  draftStorageKey,
  draftWrite,
  mayPersist,
  restoredDraft,
} from "./draft-storage";

describe("the storage key", () => {
  it("scopes a draft to its room", () => {
    expect(draftStorageKey("room-a-1")).not.toBe(draftStorageKey("room-a-2"));
  });

  it("is prefixed, so chat state is one scan to find", () => {
    expect(draftStorageKey("room")).toMatch(/^cfg\.chat\.draft\./);
  });
});

describe("restoring", () => {
  it("returns the stored draft", () => {
    expect(restoredDraft("half a sentence")).toBe("half a sentence");
  });

  it("treats an EMPTY stored value as nothing to restore", () => {
    // MUTANT: `return stored` → this dies, and the defect is silent: an empty
    // entry would call setText("") and wipe a field the host had seeded.
    expect(restoredDraft("")).toBeNull();
  });

  it("treats a missing entry as nothing to restore", () => {
    expect(restoredDraft(null)).toBeNull();
  });

  it("truncates rather than dropping an oversized draft", () => {
    // Losing the tail of a long draft beats losing all of it — the user can see
    // what survived and retype the rest.
    const long = "x".repeat(DRAFT_MAX_LENGTH + 500);
    expect(restoredDraft(long)).toHaveLength(DRAFT_MAX_LENGTH);
  });
});

describe("writing", () => {
  it("stores real text", () => {
    expect(draftWrite("draft")).toEqual({ value: "draft" });
  });

  it("REMOVES on empty, which is what clears the draft after a send", () => {
    // MUTANT: `return { value: "" }` → this dies. `send` resets the draft, so
    // the empty write IS the clear; storing "" instead would leave every sent
    // room holding a dead entry.
    expect(draftWrite("")).toEqual({ remove: true });
  });

  it("caps what it stores", () => {
    const decision = draftWrite("y".repeat(DRAFT_MAX_LENGTH + 10));
    expect("value" in decision && decision.value.length).toBe(DRAFT_MAX_LENGTH);
  });
});

describe("the save gate", () => {
  it("refuses before this room's restore has run", () => {
    // MUTANT: `return true` → this dies, and it is the destructive one. Writing
    // here stores the PREVIOUS room's text under this room's key, or erases a
    // stored draft with the emptiness that precedes its own restore.
    expect(mayPersist(null, "room-a")).toBe(false);
  });

  it("refuses while the restored room is a DIFFERENT one", () => {
    expect(mayPersist("room-a", "room-b")).toBe(false);
  });

  it("allows once the rooms agree", () => {
    expect(mayPersist("room-a", "room-a")).toBe(true);
  });
});
