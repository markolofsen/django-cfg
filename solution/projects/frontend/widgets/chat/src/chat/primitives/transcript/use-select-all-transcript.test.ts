import { describe, expect, it } from "vitest";

import { claimsSelectAll, selectTranscript } from "./use-select-all-transcript";

/**
 * Which ⌘A belongs to the transcript.
 *
 * The DOM half (`selectTranscript` building a Range) needs real
 * `Range`/`Selection`, which this app's test environment does not provide —
 * there is no `document` here at all. So the decision was split out: this
 * covers every way the feature can misbehave silently, and the browser check
 * covers that the range itself reads correctly.
 */

function key(over: Partial<Parameters<typeof claimsSelectAll>[0]> = {}) {
  return {
    key: "a",
    metaKey: true,
    ctrlKey: false,
    altKey: false,
    shiftKey: false,
    editableTarget: false,
    ...over,
  };
}

describe("claimsSelectAll", () => {
  it("takes ⌘A and Ctrl+A over the transcript", () => {
    expect(claimsSelectAll(key())).toBe(true);
    expect(claimsSelectAll(key({ metaKey: false, ctrlKey: true }))).toBe(true);
  });

  it("LEAVES ⌘A alone while the caret is in an editable", () => {
    // The composer's own select-all is the more specific intent. Taking it
    // would break ordinary typing to fix a copy — and `useHotkey`'s default
    // policy WOULD take it, since a modifier combo fires in inputs by default.
    expect(claimsSelectAll(key({ editableTarget: true }))).toBe(false);
  });

  it("ignores a bare A, so typing is never intercepted", () => {
    expect(claimsSelectAll(key({ metaKey: false }))).toBe(false);
  });

  it("ignores ⌘⇧A and ⌘⌥A, which are other commands", () => {
    expect(claimsSelectAll(key({ shiftKey: true }))).toBe(false);
    expect(claimsSelectAll(key({ altKey: true }))).toBe(false);
  });

  it("ignores another letter held with ⌘", () => {
    // The control: without this, a predicate that only checked modifiers
    // would pass every test above and hijack ⌘K.
    expect(claimsSelectAll(key({ key: "k" }))).toBe(false);
  });
});

describe("selectTranscript", () => {
  it("declines when there is no surface, so the browser keeps ⌘A", () => {
    expect(selectTranscript(null)).toBe(false);
  });
});
