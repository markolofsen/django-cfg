import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The transcript's live-region contract, as a SOURCE ratchet.
 *
 * Named honestly: this reads the file, it does not render it. The real test
 * mounts a transcript, streams a reply and asserts a screen reader hears two
 * strings rather than every token — and that needs jsdom, which does not
 * resolve from this package. A test that cannot fail for the right reason is
 * worse than an absent one, so this is scoped to what it CAN prove: that the
 * attribute which caused the defect has not come back.
 *
 * The defect: `aria-relevant` with a `text` value on the list container. It
 * asks assistive tech to announce changes to text NODES inside the region, and
 * a streamed reply rewrites its text node on every delta — so the whole answer
 * was read out token by token.
 *
 * TODO: replace with a render test once jsdom resolves here.
 */
const SOURCE = readFileSync(new URL("./transcript.tsx", import.meta.url), "utf8");

/**
 * The same source with comments removed.
 *
 * THE trap this file exists to remember. The comment above the JSX quotes the
 * forbidden attribute to explain the defect — so a check over raw text flags
 * the EXPLANATION as the defect itself, and the suite goes red before and after
 * the mutation alike. A gate that always fails proves nothing and its red gets
 * ignored, which is strictly worse than having no gate.
 */
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

describe("the comment stripper", () => {
  it("removes prose but keeps the JSX", () => {
    // The control for every assertion below. If the stripper returned "" — a
    // greedy block-comment regex does exactly that — every `not.toMatch` would
    // pass while measuring nothing.
    expect(CODE).toContain('role="log"');
    expect(CODE).toContain('role="status"');
    expect(CODE).not.toContain("token by token");
    expect(CODE.length).toBeGreaterThan(400);
  });
});

describe("transcript live region", () => {
  it("never sets aria-relevant", () => {
    // Matches the ATTRIBUTE, not the word: the comment above the JSX names it to
    // explain the defect, and a test that cannot tell code from prose would
    // forbid documenting it.
    // MUTANT: add the attribute back to the JSX → this dies.
    expect(CODE).not.toMatch(/aria-relevant\s*=/);
  });

  it("names the log, so the region is not anonymous", () => {
    expect(CODE).toContain('role="log"');
    expect(CODE).toContain("aria-label={label}");
  });

  it("keeps the announcer OUTSIDE the message list", () => {
    // A `role="status"` inside the list would inherit the same mutations the
    // list carries, which is the defect wearing a different attribute.
    const listAt = CODE.indexOf('role="log"');
    const statusAt = CODE.indexOf('role="status"');
    expect(listAt).toBeGreaterThan(-1);
    expect(statusAt).toBeGreaterThan(listAt);
  });

  it("hides the announcer with clip, not display or visibility", () => {
    // `display:none` and `visibility:hidden` remove the node from the
    // accessibility tree, taking the announcement with it.
    expect(CODE).toContain('clip: "rect(0 0 0 0)"');
    expect(CODE).not.toContain('display: "none"');
    expect(CODE).not.toContain('visibility: "hidden"');
  });

  it("announces only transitions, never the streamed text", () => {
    // The announcer's text comes from the `announce` prop's two fixed strings.
    // If a message body ever reached it, every reply would be read aloud in
    // full — the original defect through a different door.
    expect(CODE).toMatch(/setText\(isStreaming \? announce\.streaming : announce\.complete\)/);
  });
});

describe("keyboard reachability", () => {
  it("gives the list a roving tabindex rather than a tab stop per row", () => {
    // Without this, Tab walks every message and link before the composer, so on
    // a long transcript the input cannot be reached at all.
    expect(CODE).toContain("useRovingFocus(ids.length)");
    expect(CODE).toContain("roving.itemProps(index)");
    expect(CODE).toContain("onKeyDown={roving.onKeyDown}");
  });

  it("passes the row COUNT to the focus hook", () => {
    // Messages arrive while the user reads. Without the count, an active index
    // outlives its row and every row renders `tabIndex={-1}` — the transcript
    // silently stops being reachable by Tab and nothing looks broken.
    expect(CODE).toMatch(/useRovingFocus\(\s*ids\.length\s*\)/);
  });
});

describe("returning to the bottom", () => {
  it("offers the jump control ONLY while scrolled away", () => {
    // A permanent button is noise; an absent one strands a user who scrolled up
    // during a long reply, chasing a bottom that keeps moving.
    expect(CODE).toContain("!isPinned && jumpToLatest !== undefined");
    expect(CODE).toContain("jumpToLatest({ onClick: scrollToBottom, missed })");
  });

  /**
   * Anchored to the SCROLLER's lower edge, never the chat's: the chat's last
   * grid row is the composer, which grows as the user types, so a control
   * positioned against it drifts and eventually covers the input.
   */
  it("anchors the control to the scroller, not the chat", () => {
    expect(CODE).toContain("relative h-0");
  });

  /**
   * The count rides the same render prop rather than a second subscription, so
   * a host cannot render a button whose badge disagrees with its own visibility.
   */
  it("hands the host the missed count with the control", () => {
    expect(CODE).toContain("useMissedCount(ids, isPinned)");
  });
});
