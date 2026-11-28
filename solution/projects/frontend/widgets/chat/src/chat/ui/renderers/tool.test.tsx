import { readFileSync } from "node:fs";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ChatMessage, MessagePart } from "../../core";
import { ToolRenderer, keepsOverride, opensItself } from "./tool";

/**
 * A tool call is a summary that opens.
 *
 * Two kinds of gate here, because the rule has two halves that fail
 * differently. The DISCLOSURE rule is a pure function and is tested as one. The
 * WRAP is CSS — no assertion on rendered markup can see it, so it is read from
 * the stylesheet, which is the only place the fact lives.
 */

const message = { id: "m1", role: "assistant", parts: [] } as unknown as ChatMessage;

const toolPart = (state: string, extra: Record<string, unknown> = {}): MessagePart =>
  ({
    type: "tool",
    id: "t1",
    toolName: "tool_search",
    toolState: { state, input: { query: "audio" }, ...extra },
  }) as unknown as MessagePart;

const render = (part: MessagePart) =>
  renderToStaticMarkup(<ToolRenderer part={part} message={message} />);

const read = (path: string) => readFileSync(new URL(path, import.meta.url), "utf8");

const STYLES = read("../../../styles/tool.css");
const INDEX = read("../../../styles/index.css");

describe("the disclosure rule", () => {
  it("opens a call while it runs", () => {
    // The whole reason the part renders at `tool-input-start` is that the reader
    // sees WHICH tool is working. Folded shut, a running call is
    // indistinguishable from a stalled one.
    // MUTANT: `state !== "input-streaming"` → this dies.
    expect(opensItself("input-streaming")).toBe(true);
    expect(opensItself("input-available")).toBe(true);
  });

  it("shuts a call that succeeded", () => {
    // The case that motivated the rule: one `tool_search` result filled the
    // viewport and buried the answer under it.
    // MUTANT: return true unconditionally → this dies.
    expect(opensItself("output-available")).toBe(false);
  });

  it("leaves an error open", () => {
    // Short, and the reason the turn went the way it did — the one output worth
    // the reader's screen unprompted.
    // MUTANT: fold errors in with completions → this dies.
    expect(opensItself("output-error")).toBe(true);
  });
});

describe("a reader's click", () => {
  it("survives renders that do not change the state", () => {
    // The click is only useful if it outlives the token stream that follows it.
    // MUTANT: `return false` → this dies, and the box reverts on every render.
    expect(keepsOverride("input-available", "input-available")).toBe(true);
  });

  it("yields to the transition that carries its own answer", () => {
    // Arriving at a result is the one moment the rule has a better answer than
    // the reader's earlier click: the call finished, so it folds away.
    // MUTANT: `return true` → this dies, and nothing ever auto-collapses.
    expect(keepsOverride("input-available", "output-available")).toBe(false);
    expect(keepsOverride("input-streaming", "input-available")).toBe(false);
  });
});

describe("what the collapsed call renders", () => {
  it("draws no body when it is shut", () => {
    // Absent, not hidden: a `hidden` subtree still carries the tall result this
    // rule exists to remove.
    // MUTANT: render the body unconditionally → this dies.
    const html = render(toolPart("output-available", { output: "five tool descriptions" }));
    expect(html).not.toContain("five tool descriptions");
  });

  it("draws the body while it runs", () => {
    const html = render(toolPart("input-available"));
    expect(html).toContain("audio");
  });

  it("names the disclosure for a screen reader in both states", () => {
    // The chevron is decorative, so the accessible name is the only thing a
    // reader has to go on.
    // MUTANT: drop `aria-label` → this dies.
    expect(render(toolPart("input-available"))).toContain("aria-label");
    expect(render(toolPart("output-available"))).toContain("aria-label");
  });

  it("marks the open state as data for the stylesheet", () => {
    // The chevron rotation is CSS keyed on `data-open`; without the attribute
    // the arrow points down on an open call.
    // MUTANT: stop passing `open` to `ToolCall` → this dies.
    expect(render(toolPart("input-available"))).toContain("data-open");
    expect(render(toolPart("output-available"))).not.toContain("data-open");
  });
});

describe("the stylesheet carries the wrap and the cap", () => {
  it("every source read has content after stripping comments", () => {
    // The control. A ratchet over an empty read passes vacuously, and these are
    // the only assertions in the file that no rendered markup can confirm.
    for (const source of [STYLES, INDEX]) {
      const code = source.replace(/\/\*[\s\S]*?\*\//g, "").trim();
      expect(code.length).toBeGreaterThan(0);
    }
  });

  it("breaks an unbreakable token in tool output", () => {
    // The defect on the screenshot: a path and a datamarked transcript carry no
    // break opportunity, so the box grew until the text left it.
    // MUTANT: delete the rule → this dies.
    expect(STYLES).toMatch(/\.chat-tool-output[\s\S]*?overflow-wrap:\s*anywhere/);
    expect(STYLES).toMatch(/\.chat-tool-input[\s\S]*?overflow-wrap:\s*anywhere/);
  });

  it("caps an open result rather than letting it fill the page", () => {
    // MUTANT: drop `max-height` → this dies.
    expect(STYLES).toMatch(/\.chat-tool-output\s*\{[^}]*max-height/);
  });

  it("never caps an error", () => {
    expect(STYLES).toMatch(/\[data-error\][\s\S]*?max-height:\s*none/);
  });

  it("turns the running marker rather than pulsing it", () => {
    // One motion vocabulary: the turn mark, the recording glyph and this share
    // `turn-mark-tumble`. A pulse says only "busy"; rotation has a direction, so
    // a glance separates live from stalled.
    // MUTANT: swap the animation for a pulse → this dies.
    expect(STYLES).toMatch(/\.chat-tool-dot\[data-running\][\s\S]*?turn-mark-tumble/);
    expect(STYLES).not.toMatch(/animate-pulse|pulse\s+\d/);
  });

  it("squares the marker while it turns", () => {
    // The reference's measured point: corners are what make rotation visible,
    // and a turning circle at this size is indistinguishable from a still one.
    // MUTANT: keep `border-radius: 999px` while running → this dies.
    expect(STYLES).toMatch(/\.chat-tool-dot\[data-running\]\s*\{[^}]*border-radius:\s*0\./);
  });

  it("marks a running call as data for the stylesheet", () => {
    // MUTANT: drop `data-running` → this dies, and the marker never turns.
    expect(render(toolPart("input-available"))).toContain("data-running");
    expect(render(toolPart("output-available"))).not.toContain("data-running");
  });

  it("marks a running call at the size of the BLOCK, not the glyph", () => {
    // An 8px marker put the whole signal in the smallest element on the row, so
    // a running call and a finished one read as the same card at a glance.
    // MUTANT: delete the border rule → this dies.
    expect(STYLES).toMatch(
      /\.chat-tool\[data-state="input-available"\][\s\S]*?border-color/,
    );
  });

  it("accents the status word while it runs", () => {
    // "Running" in the same grey as "Done" states the fact and hides it. The
    // selector carries (0,3,0) against the utility's (0,1,0), so it wins without
    // depending on source order — the tie that once turned the mic glyph white.
    // MUTANT: drop the rule → this dies.
    expect(STYLES).toMatch(
      /\.chat-tool\[data-state="input-available"\]\s+\.chat-tool-status/,
    );
    expect(render(toolPart("input-available"))).toContain("chat-tool-status");
  });

  it("separates consecutive calls", () => {
    // Four bordered boxes at a 4px gap read as one striped block rather than as
    // four events. The rule moved to `block.css` when cards and pictures needed
    // the same rhythm — a tool call next to a card must not be spaced by two
    // files that happen to agree. `blocks-are-spaced.test.ts` owns the pairings;
    // this asserts the tool half still resolves.
    // MUTANT: delete the adjacent-sibling rule → this dies.
    expect(read("../../../styles/block.css")).toMatch(
      /\.chat-tool\s*\+\s*\.chat-tool[\s\S]*?margin-block-start/,
    );
  });

  it("is imported, or none of the above reaches a browser", () => {
    // The rule this file is most likely to get wrong: every assertion above
    // passes against a stylesheet nothing loads.
    // MUTANT: remove the @import → this dies.
    expect(INDEX).toContain('@import "./tool.css"');
  });
});
