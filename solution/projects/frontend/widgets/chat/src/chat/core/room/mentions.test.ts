/* eslint-disable no-irregular-whitespace -- the cases type a no-break space on purpose */
import { describe, expect, it } from "vitest";
import { applyTrigger, detectTrigger } from "./mentions";

/**
 * Detection is pure, so it is tested without an editor — which is the whole
 * reason it lives in core/. The editor surface is expected to be replaced
 * (textarea → Tiptap); these tests must not be.
 *
 * The unicode-whitespace cases are taken from assistant-ui's own test file
 * (MIT). They are the ones nobody derives from first principles: an IME
 * full-width space and an NBSP are whitespace to a user and to `\s`, and a
 * detector that only knows ASCII space fails on Japanese input.
 */

describe("detectTrigger", () => {
  it("detects a query at the caret", () => {
    expect(detectTrigger("hello @wor", "@", 10)).toEqual({ query: "wor", offset: 6 });
  });

  it("matches at the very start of the text", () => {
    expect(detectTrigger("@wor", "@", 4)).toEqual({ query: "wor", offset: 0 });
  });

  it("returns an empty query right after the trigger, so the menu opens", () => {
    // The menu must appear on "@" alone — waiting for a first letter makes the
    // feature undiscoverable.
    expect(detectTrigger("hi @", "@", 4)).toEqual({ query: "", offset: 3 });
  });

  it("requires whitespace before the trigger, so an email is not a mention", () => {
    // The case that makes a naive indexOf unusable: every keystroke of an
    // address would open the menu.
    expect(detectTrigger("mail@example.com", "@", 16)).toBeNull();
  });

  it("ignores a trigger after the caret", () => {
    expect(detectTrigger("hi @bob", "@", 2)).toBeNull();
  });

  it("finds the trigger closest to the caret", () => {
    expect(detectTrigger("@a @b", "@", 5)).toEqual({ query: "b", offset: 3 });
  });

  it("stops at a newline even when spaces are allowed", () => {
    // A mention cannot span a paragraph; allowing it keeps the menu open
    // forever after any unmatched "@".
    expect(detectTrigger("@a\nb", "@", 4, { allowSpaces: true })).toBeNull();
  });

  it("treats a tab as a boundary on both sides", () => {
    expect(detectTrigger("a\t@b", "@", 4)).toEqual({ query: "b", offset: 2 });
    expect(detectTrigger("@a\tb", "@", 4)).toBeNull();
  });

  describe("unicode whitespace", () => {
    it("accepts a full-width space (U+3000) as a boundary", () => {
      // An IME emits this instead of a plain space. A detector that only knows
      // ASCII refuses to open the menu for a Japanese-input user.
      // Indices: 0=あ 1=　(U+3000) 2=@ 3=b — so the trigger is at 2.
      expect(detectTrigger("あ　@b", "@", 4)).toEqual({ query: "b", offset: 2 });
    });

    it("accepts an NBSP as a boundary", () => {
      expect(detectTrigger("a @b", "@", 4)).toEqual({ query: "b", offset: 2 });
    });

    it("ends a strict query at a full-width space", () => {
      expect(detectTrigger("@a　b", "@", 4)).toBeNull();
    });

    it("does not match a full-width ＠ against an ASCII trigger", () => {
      // Literal comparison. Matching them would make the two indistinguishable
      // in the text that is finally sent.
      expect(detectTrigger("hi ＠bob", "@", 7)).toBeNull();
    });
  });

  describe("allowSpaces — for machine names, which contain them", () => {
    it("keeps matching across a space", () => {
      // "Mark's MacBook" is a real machine name. A strict scan closes the menu
      // mid-name, exactly when the user still needs it.
      expect(detectTrigger("@Mark's Mac", "@", 11, { allowSpaces: true })).toEqual({
        query: "Mark's Mac",
        offset: 0,
      });
    });

    it("gives up after maxWords, so a stale @ cannot match forever", () => {
      // Without the bound, an unmatched "@" earlier in a paragraph keeps
      // matching for the rest of the message.
      expect(
        detectTrigger("@a b c d e", "@", 10, { allowSpaces: true, maxWords: 3 }),
      ).toBeNull();
    });

    /**
     * ON the bound, not two words past it. The old test used five words against
     * `maxWords: 3` and so could not see that the counter was off by one: it
     * counted GAPS with a `>` comparison, and three gaps means four words. In a
     * live composer that let the menu keep matching a whole word after it should
     * have closed.
     */
    it("allows exactly maxWords and refuses the next one", () => {
      const opts = { allowSpaces: true, maxWords: 3 };
      expect(detectTrigger("@a b c", "@", 6, opts)?.query).toBe("a b c");
      expect(detectTrigger("@a b c d", "@", 8, opts)).toBeNull();
    });

    /**
     * A run of spaces is ONE gap. Counting whitespace CHARACTERS made the bound
     * depend on how the user spaced their text: `@a  b  c  d` closed while
     * `@a b c d` — the same four words — stayed open.
     */
    it("counts a run of spaces as one word boundary", () => {
      const opts = { allowSpaces: true, maxWords: 3 };
      expect(detectTrigger("@a  b  c", "@", 8, opts)?.query).toBe("a  b  c");
      expect(detectTrigger("@a  b  c  d", "@", 11, opts)).toBeNull();
    });

    it("still refuses a mid-word trigger", () => {
      expect(detectTrigger("mail@a b", "@", 8, { allowSpaces: true })).toBeNull();
    });
  });

  describe("multi-character triggers", () => {
    it("matches one and reports the trigger's own offset", () => {
      expect(detectTrigger("hi ::cmd", "::", 8)).toEqual({ query: "cmd", offset: 3 });
    });
  });

  it("survives edge inputs without throwing", () => {
    expect(detectTrigger("", "@", 0)).toBeNull();
    expect(detectTrigger("abc", "", 3)).toBeNull();
    expect(detectTrigger("@a", "@", 99)).toEqual({ query: "a", offset: 0 });
    expect(detectTrigger("@a", "@", -5)).toBeNull();
  });
});

describe("applyTrigger", () => {
  it("replaces the query and leaves the caret past a trailing space", () => {
    // The space is part of the replacement: without it the caret sits against
    // the inserted name and the next character types into a finished mention.
    const match = detectTrigger("hi @bo", "@", 6);
    expect(match).not.toBeNull();

    expect(applyTrigger("hi @bo", match!, 6, "@bob")).toEqual({
      text: "hi @bob ",
      caret: 8,
    });
  });

  it("keeps text that follows the caret", () => {
    const match = detectTrigger("@bo rest", "@", 3);
    expect(applyTrigger("@bo rest", match!, 3, "@bob")).toEqual({
      text: "@bob  rest",
      caret: 5,
    });
  });
});
