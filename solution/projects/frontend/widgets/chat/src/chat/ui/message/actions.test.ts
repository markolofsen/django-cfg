import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import type { ChatMessage, MessagePart } from "../../core/conversation/parts";
import { messageCopyText } from "./actions";

/**
 * What Copy puts on the clipboard is behaviour and gets a real test; where the
 * row sits and how it reveals is CSS the package has no DOM to observe, and
 * gets a source ratchet — the same split `message.bubble.test.ts` makes, and
 * for the same reason: the alternative to reading the source is not a better
 * test, it is no test.
 */

const message = (parts: readonly MessagePart[]): ChatMessage => ({
  id: "m1",
  role: "assistant",
  parts,
  status: { state: "complete" },
  createdAt: 0,
});

describe("what Copy actually copies", () => {
  it("joins text parts, separated as paragraphs", () => {
    const text = messageCopyText(
      message([
        { id: "p1", type: "text", text: "first" },
        { id: "p2", type: "text", text: "second" },
      ]),
    );
    expect(text).toBe("first\n\nsecond");
  });

  /**
   * Reasoning collapses by default and is never the answer the reader means.
   * Including it would put the model's thinking into a paste of its reply.
   */
  it("excludes reasoning", () => {
    const text = messageCopyText(
      message([
        { id: "p1", type: "reasoning", text: "considering the options" },
        { id: "p2", type: "text", text: "the answer" },
      ]),
    );
    expect(text).toBe("the answer");
  });

  /**
   * A tool call's rendered form is not its data. Copying a diff card as JSON is
   * worse than offering nothing.
   */
  it("excludes tool calls and typed blocks", () => {
    const text = messageCopyText(
      message([
        {
          id: "p1",
          type: "tool",
          toolName: "read_file",
          toolState: { state: "output-available", input: {}, output: "x" },
        },
        { id: "p2", type: "data", kind: "diff", data: {} },
        { id: "p3", type: "text", text: "done" },
      ]),
    );
    expect(text).toBe("done");
  });

  /**
   * The empty result is load-bearing: `useCopyAction` returns no descriptor for
   * it, so a turn that is only a tool call offers no control rather than a
   * control that writes an empty string.
   */
  it("is empty for a turn with no text at all", () => {
    expect(messageCopyText(message([{ id: "p1", type: "data", kind: "diff", data: {} }]))).toBe("");
  });

  /**
   * A turn that HAS a text part carrying nothing yet.
   *
   * This is the shape a turn takes between "the part exists" and "the first
   * token arrived", and `isTextPart` accepts it — the filter keys on `type`,
   * not on content. Without the trim the join returns "" anyway, but stating it
   * pins WHY the empty control never appears for a turn showing only a spinner.
   */
  it("is empty for a text part that has not received a token yet", () => {
    expect(messageCopyText(message([{ id: "p1", type: "text", text: "" }]))).toBe("");
  });
});

const SOURCE = readFileSync(new URL("./actions.tsx", import.meta.url), "utf8");
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

describe("comment stripper (control)", () => {
  it("leaves real code behind", () => {
    expect(CODE).toContain("export function MessageActions");
  });
});

describe("a turn still being written offers no control", () => {
  /**
   * MUTANT: drop the `streaming` guard → this dies.
   *
   * Text length alone was the whole condition, and a streaming turn has text
   * from its first token — so the control appeared over a half-written answer
   * and copied whatever had arrived by the instant of the click. It also
   * appeared over a turn showing only "Thinking", because a reasoning part is
   * accompanied by an empty text part.
   */
  it("withholds Copy while the turn is streaming", () => {
    expect(CODE).toContain('message.status.state === "streaming"');
  });

  /**
   * `interrupted` and `failed` KEEP the control. Both are final, their text is
   * whatever the turn managed to produce, and that is exactly what a reader
   * wants to salvage. Only `streaming` is a moving target — a guard written as
   * `!== "complete"` would take the control away from the two states where it
   * matters most.
   */
  it("withholds it for streaming ONLY, not for every non-complete state", () => {
    expect(CODE).not.toContain('!== "complete"');
    expect(CODE).not.toContain('=== "interrupted"');
  });
});

describe("the row is reachable without a pointer", () => {
  /**
   * Hover alone makes these controls unreachable by keyboard — the same defect
   * the diff widget's scroll region had to repair.
   */
  it("reveals on focus as well as hover", () => {
    expect(CODE).toContain("group-hover:opacity-100");
    expect(CODE).toContain("group-focus-within:opacity-100");
  });

  it("names every control, since the row is icon-only", () => {
    expect(CODE).toContain("aria-label={action.label}");
  });

  it("keeps a hidden row from swallowing clicks aimed at the text", () => {
    expect(CODE).toContain("pointer-events-none");
  });
});

describe("the toolbar is static, and its height is given back", () => {
  /**
   * In flow, so it belongs to the message it acts on — an overlaid row reads as
   * floating chrome. It never mounts on hover, which would push the transcript
   * under the pointer already there.
   */
  it("holds its place in flow rather than floating", () => {
    expect(CODE).toContain("h-7");
    expect(CODE).not.toContain("absolute");
  });

  /**
   * Faint, not invisible: at zero the control cannot be discovered without
   * hovering every message, so a first-time reader never learns it exists.
   */
  it("is faint by default and full on hover or focus", () => {
    expect(CODE).toContain("opacity-10");
    expect(CODE).toContain("group-hover:opacity-100");
    expect(CODE).toContain("group-focus-within:opacity-100");
  });
});

describe("the inventory belongs to the host", () => {
  /**
   * A flag per action is the shape that cannot express an action the package
   * has never heard of, and grows one prop per feature.
   */
  it("takes a list of actions, not a boolean per action", () => {
    expect(CODE).toContain("actions: readonly MessageAction[]");
    expect(CODE).not.toMatch(/show(Copy|Retry|Edit)/);
  });

  it("renders nothing rather than an empty row", () => {
    expect(CODE).toContain("actions.length === 0");
  });

  /**
   * The clipboard is injected. Importing one would give this package a
   * clipboard implementation and a second consumer no way to replace it.
   */
  it("does not import a clipboard", () => {
    expect(CODE).not.toContain("navigator.clipboard");
    expect(CODE).toContain("write: (text: string) => Promise<boolean>");
  });
});

/**
 * The action row names its controls the way every other icon-only control in
 * a host does.
 */
describe("the action row's hover names", () => {
  it("uses the design-system tooltip, not the native title", () => {
    // `title` is the OS bubble: it ignores the theme, waits about a second, and
    // would leave this the one control still using it. Removing it is half the
    // change — without the wrapper the button would have no hover name at all.
    expect(CODE).toContain("<TooltipHint key={action.id} tooltip={action.label}");
    expect(CODE).not.toContain("title={action.label}");
  });

  it("keeps the accessible name on the button itself", () => {
    // The tooltip is a pointer affordance. A disabled button fires no pointer
    // events, so `aria-label` is the only name a screen reader or a disabled
    // control has — dropping it would trade one audience for another.
    expect(CODE).toContain("aria-label={action.label}");
  });
});
