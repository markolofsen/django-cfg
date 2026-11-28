import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * The store must survive a re-render. A SOURCE ratchet, deliberately.
 *
 * ## The defect this guards
 *
 * `ChatProvider` used to build its store inside
 * `useMemo(..., [adapter, capabilities, store])`. `capabilities` is an object
 * literal at every realistic call site — `<ChatProvider capabilities={{
 * attachments: true }}>` — so it is a new reference on every parent render, the
 * memo recomputes, and a NEW store means an EMPTY transcript. The conversation
 * disappears mid-turn with no error and nothing in the stack pointing here.
 *
 * ## Why source and not behaviour
 *
 * The honest test renders the provider twice with a fresh `capabilities` object
 * and asserts the store identity held. That needs a DOM: `@testing-library/react`
 * and `jsdom` do not resolve from this package (`react-dom/server` does, but SSR
 * renders once and so cannot observe stability ACROSS renders — a test that
 * cannot fail for the right reason is worse than none).
 *
 * So this reads the source instead, and says so. It is a weaker instrument and
 * the weakness is named rather than hidden: it cannot catch a store rebuilt some
 * OTHER way. It does catch the exact regression that shipped — the memo coming
 * back — which is the one a later "tidy up the hooks" pass would reintroduce.
 *
 * **Replace this with a render test the moment jsdom lands in this package.**
 * That is a real to-do, not a ritual disclaimer.
 */

const SOURCE = readFileSync(join(__dirname, "provider.tsx"), "utf8");

describe("ChatProvider store stability", () => {
  it("creates the store in a ref, never in a memo", () => {
    // MUTANT: move createChatStore back inside useMemo → this dies.
    const memoBody = /useMemo\(\s*\(\)\s*=>\s*\{?[\s\S]*?\}?\s*,\s*\[[^\]]*\]\s*\)/g;
    for (const match of SOURCE.match(memoBody) ?? []) {
      expect(
        match.includes("createChatStore"),
        "createChatStore is inside a useMemo — a new `capabilities` literal " +
          "would rebuild the store and empty the transcript",
      ).toBe(false);
    }
    expect(SOURCE).toContain("useRef<ChatStore | null>(null)");
  });

  it("does not key anything on the capabilities object for the store's life", () => {
    // The store's creation must not read `capabilities` at all: it is the prop
    // most likely to be a fresh literal, and the least related to store identity.
    const creation = SOURCE.slice(
      SOURCE.indexOf("const ownStore"),
      SOURCE.indexOf("const active"),
    );
    expect(creation.length).toBeGreaterThan(0);
    // MUTANT: pass capabilities into createChatStore → this dies.
    expect(creation).not.toContain("capabilities");
  });

  it("sends through the LIVE adapter, not the one captured at mount", () => {
    // The store is built once, so passing `adapter` straight in freezes the
    // first one. A host re-binds its adapter when the room changes, and the
    // frozen one still addresses the room open at mount: the start screen's
    // first message landed in the previous conversation instead of creating one.
    const creation = SOURCE.slice(
      SOURCE.indexOf("const ownStore"),
      SOURCE.indexOf("const active"),
    );
    // MUTANT: pass `adapter` directly → this dies.
    expect(creation).toMatch(/adapter:\s*\{/);
    expect(creation).toContain("liveAdapter.current");
    // The ref must be refreshed on every render, or it is the mount capture
    // under a different name.
    expect(SOURCE).toContain("liveAdapter.current = adapter");
  });

  it("still follows an explicitly swapped store prop", () => {
    // The one identity that SHOULD be followed: a caller handing in a different
    // store means it. MUTANT: drop `store ??` → this dies.
    expect(SOURCE).toContain("store ?? ownStore.current");
  });
});
