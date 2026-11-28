import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The consumer ratchet, generalised: a control the package ships must be
 * MOUNTED by the assembly, not merely exported.
 *
 * Four subsystems shipped complete — component, store, tests, docs — and
 * rendered for nobody, because the only host composed the primitives by hand
 * and forgot them: voice, attachments, the jump-to-latest control, and the
 * prompt queue. Nothing failed in any of those cases. Types were clean and every
 * test was green; the feature simply did not exist for a user.
 *
 * A unit test cannot see this, because the unit was never the problem. What
 * makes the check possible now is that there IS one assembly per surface — while
 * hosts hand-composed, "the assembly" was whichever file each host wrote, and
 * nothing could name it.
 */

const read = (name: string) =>
  readFileSync(new URL(name, import.meta.url), "utf8")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/\/\/.*$/gm, "");

const COMPOSER = read("./chat/composer.tsx");
const TRANSCRIPT = read("./transcript/transcript.tsx");

describe("the ratchet reads real code (control)", () => {
  it("both assemblies have content after stripping comments", () => {
    // Every `toContain` below passes vacuously on "". A greedy block-comment
    // regex returns exactly that.
    expect(COMPOSER.length, "composer read as empty").toBeGreaterThan(400);
    expect(TRANSCRIPT.length, "transcript read as empty").toBeGreaterThan(400);
  });
});

describe("the composer assembly mounts every control it ships", () => {
  // Each of these was, at some point, exported and rendered by nobody.
  const MOUNTED = [
    "<ComposerQueue",
    "<ComposerField",
    "<ComposerVoice",
    "<ComposerSend",
    // The room-wide offer. Self-gating — nothing renders unless the room is
    // empty — so an unmounted one is invisible.
    "<ChatSuggestions",
  ];

  it.each(MOUNTED)("mounts %s", (tag) => {
    // MUTANT: delete the tag from chat-composer.tsx → this dies.
    expect(COMPOSER).toContain(tag);
  });

  it("uses the assembled field, never the bare input", () => {
    // `ComposerInput` is the lower seam: it knows nothing about mentions,
    // commands or recall. An assembly built on it looks complete and silently
    // drops three keyboard surfaces.
    expect(COMPOSER).not.toContain("<ComposerInput");
  });

  // The reading column used to be the HOST's to remember — `surface.css` asked
  // it to put the class on its own wrapper. Forgetting is silent: nothing
  // fails, the composer and the transcript just sit at different widths and the
  // conversation stops having one edge.
  it("carries the reading column itself", () => {
    expect(COMPOSER).toContain("chat-column");
  });

  // A room-wide surface that grows upward from this element (`bottom-full`)
  // needs a positioned ancestor. With none it resolves against the VIEWPORT and
  // lands away from the conversation it belongs to — visible only in a
  // locale-independent way nothing else asserts.
  it("is the positioning ancestor an upward-growing surface needs", () => {
    expect(COMPOSER).toMatch(/chat-column[^"]*relative|relative[^"]*chat-column/);
  });

  // Room-wide surfaces reach the column through this slot. Without it a host
  // renders them outside, at a different width — which is what the wrapper it
  // replaced was doing by hand.
  it("offers the above-the-field slot", () => {
    expect(COMPOSER).toContain("{above}");
  });
});

describe("the transcript assembly mounts every control it ships", () => {
  it("offers the jump-to-latest control", () => {
    // MUTANT: drop the `jumpToLatest` prop → this dies. The mechanism shipped
    // with zero consumers: `useStickToBottom`, `isPinned` and `scrollToBottom`
    // all existed and no surface rendered a button.
    expect(TRANSCRIPT).toContain("jumpToLatest=");
    expect(TRANSCRIPT).toContain("<JumpToLatest");
  });

  it("shows that a turn is in flight before any token arrives", () => {
    expect(TRANSCRIPT).toContain("pending=");
    expect(TRANSCRIPT).toContain("<PendingIndicator");
  });

  it("renders the styled row, so a user turn gets its bubble", () => {
    // The headless `<Message>` carries no bubble decision; a transcript built on
    // it renders ask and answer identically.
    expect(TRANSCRIPT).toContain("<ChatMessageView");
  });

  it("passes the footer slot through to the row", () => {
    // Without this the host's action row has nowhere to land, and Copy is
    // reachable from no message.
    expect(TRANSCRIPT).toMatch(/footer=\{footer\}/);
  });
});

describe("the data renderer draws blocks, never controls", () => {
  const DATA = read("./renderers/data.tsx");

  it("reads real code (control)", () => {
    expect(DATA.length).toBeGreaterThan(400);
  });

  it("renders media and nothing that acts on the room", () => {
    // A control drawn INSIDE the record scrolls away from the surface it acts
    // on and stays in the history forever after being used. Room-wide surfaces
    // belong above the composer; the transcript renders only what was said.
    expect(DATA).toContain("MediaWidget");
    expect(DATA).not.toMatch(/onApply|onSelect|<button/);
  });
});

describe("the assemblies carry no copy of their own", () => {
  const FILES = ["./chat/composer.tsx", "./transcript/transcript.tsx"].filter((name) => existsSync(new URL(name, import.meta.url)));

  it("sees both assembly files", () => {
    // The control: a renamed file would leave the loop below measuring nothing.
    expect(FILES.length).toBeGreaterThanOrEqual(2);
  });

  it.each(["./chat/composer.tsx", "./transcript/transcript.tsx"])(
    "%s reads no translator",
    (name) => {
      // The package ships no locales. A `t()` here would be a permanent English
      // string inside a product carrying 17 catalogues — labels arrive as props.
      expect(read(name)).not.toMatch(/useTranslation|\bt\(["'`]/);
    },
  );
});
