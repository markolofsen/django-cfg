import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ChatMessage, MessagePart, RunPart } from "../../core/conversation/parts";
import { planRuns } from "../../core/run/segment";
import { MessageContent, PartRegistryProvider } from "../../primitives";
import { RunBlock } from "./block";
import { createRunRenderer } from "./renderer";
import { step } from "./stories/steps";

const run = (parts: MessagePart[]): RunPart => ({ type: "run", id: "run", parts });
const html = (parts: MessagePart[], options = {}) => renderToStaticMarkup(<RunBlock run={run(parts)} options={options} />);

const settled = [step("s1", { label: "Searching the knowledge base", duration_ms: 900 }), step("s2", { label: "Opening the policy", duration_ms: 400 })];

describe("a settled run", () => {
  it("is one collapsed quiet line: no timeline, aria-expanded false, the summary as the name", () => {
    const out = html(settled);
    expect(out).toContain('aria-expanded="false"');
    expect(out).toContain("Worked for 1s");
    expect(out).not.toContain("chat-run-steps");
    expect(out).not.toContain("tools used");
  });

  it("an open list is one line per step: no status word, no duration, a server-named object as a chip", () => {
    const out = html([step("s1", { name: "read_page", duration_ms: 2000, refs: [{ kind: "page", id: "p", title: "Sales" }] }), step("s2", { name: "kb_search", label: "Searching the knowledge base", duration_ms: 900 })], { defaultOpen: true });
    expect(out).toContain('<span class="chat-run-object" data-named="true">Sales</span>');
    expect(out).toContain("Read ");
    expect(out).toContain("Searching the knowledge base");
    for (const noise of ["Done", "2.0s", "900ms", "chat-run-status", "chat-run-time", "data-density"]) expect(out).not.toContain(noise);
  });

  it("has no card and no toolbar row: one copy button, only inside the opened list", () => {
    expect(html(settled)).not.toContain("chat-run-copy");
    const out = html(settled, { defaultOpen: true });
    expect(out).toContain('class="chat-run-copy"');
    expect(out.indexOf("chat-run-copy")).toBeGreaterThan(out.indexOf("chat-run-steps"));
    expect(out).not.toContain("chat-run-actions");
    expect(out).not.toMatch(/Export|Compact/);
  });

  it("renders nothing for a run with no steps", () => {
    expect(html([{ type: "text", id: "t", text: "x" }])).toBe("");
  });
});

describe("a run with a failed step", () => {
  const failed = [...settled, step("s3", { status: "error", label: "Looking up the customer", error: { code: "upstream", retryable: true }, summary: "The CRM did not answer" })];

  // MUTANT: open only on a click -> a failure hides behind a closed line.
  it("opens itself, shows the timeline in arrival order and the failed step open", () => {
    const out = html(failed);
    expect(out).toContain('aria-expanded="true"');
    expect(out.indexOf("Searching the knowledge base")).toBeLessThan(out.indexOf("Opening the policy"));
    expect(out.indexOf("Opening the policy")).toBeLessThan(out.indexOf("Looking up the customer"));
    expect(out).toContain("The CRM did not answer");
    expect(out).toContain("Can be retried");
    expect(out).toContain("Worked for 1s · 1 failed");
  });
});

describe("accessibility", () => {
  it("names the timeline, gives every toggle aria-expanded and aria-controls, and shows status as a word", () => {
    const out = html([step("s1", { args: { q: "x" } }), step("s2", { status: "error", args: { q: "y" } })]);
    expect(out).toContain('aria-label="Work on this answer"');
    expect(out).toMatch(/aria-controls="[^"]+"/);
    expect(out).toContain("Failed");
    expect(out).not.toContain("Done");
    expect(out).toContain("data-run-toggle");
  });

  it("announces a settled run once through a polite status region, and stays silent while it works", () => {
    expect(html(settled)).toMatch(/role="status">Worked for 1s/);
    expect(html([step("s1", { status: "running" })])).toMatch(/role="status"><\/span>/);
  });
});

describe("privacy in the markup", () => {
  const open = [step("s1", { status: "error", args: { q: "SECRET-ARG" }, result: { preview: "SECRET-RESULT", size: 3 } })];

  it("shows argument names, a preview, and never a hidden value", () => {
    const out = html(open);
    expect(out).toContain("<code>q</code>");
    expect(out).toContain("SECRET-RESULT");
    expect(out).not.toContain("SECRET-ARG");
  });

  // MUTANT: read labelsOnly nowhere -> a public chat shows the server's detail.
  it("a public chat shows labels only: no toggle, no detail", () => {
    const out = html(open, { labelsOnly: true });
    expect(out).not.toContain("SECRET");
    expect(out).not.toContain("data-run-toggle");
  });

  it("the copy button is absent when the host turns copy off", () => {
    expect(html(open, { allowCopy: false, defaultOpen: true })).not.toContain("Copy trace");
    expect(html(open, { defaultOpen: true })).toContain("Copy trace");
  });
});

describe("a thought's words", () => {
  // A failed step opens the block, so the timeline (where the tail lives) is in the markup.
  const thinking = (streaming: boolean): MessagePart[] => [step("s1", { status: "error" }), { type: "reasoning", id: "r", text: "x".repeat(600), streaming, meta: { status: streaming ? "running" : "ok", redaction: "none" } }];

  it("are not shown by default", () => {
    expect(html(thinking(true))).not.toContain("xxxx");
  });

  it("show in a bounded box while it streams when the host allows them", () => {
    const out = html(thinking(true), { showReasoningText: true });
    expect(out).toContain("chat-run-thought");
    expect(out).toContain("x".repeat(600));
  });

  it("are capped in the DOM at the latest 8 000 characters", () => {
    const long: MessagePart[] = [step("s1", { status: "error" }), { type: "reasoning", id: "r", text: `${"o".repeat(5000)}${"n".repeat(8000)}`, streaming: true, meta: { status: "running", redaction: "none" } }];
    const out = html(long, { showReasoningText: true });
    expect(out).not.toContain("ooo");
    expect(out).toContain(`…${"n".repeat(8000)}`);
  });

  it("a settled thought is a line named by its summary, closed until the reader opens it", () => {
    const done: MessagePart[] = [step("s1", { status: "error" }), { type: "reasoning", id: "r", text: "words", streaming: false, meta: { status: "ok", summary: "Considering user needs for visuals", redaction: "none" } }];
    const out = html(done, { showReasoningText: true });
    expect(out).toContain("Considering user needs for visuals");
    expect(out).not.toContain("chat-run-thought");
  });
});

describe("paging", () => {
  it("offers 'Show N more' past a page, and counts the remainder", () => {
    const parts = Array.from({ length: 40 }, (_, i) => step(`s${i + 1}`));
    const out = renderToStaticMarkup(<RunBlock run={run([...parts, step("s99", { status: "error" })])} />);
    expect(out).toContain("Show 15 more");
    expect(out.match(/chat-run-step"/g)).toHaveLength(26);
  });
});

describe("the stored trace", () => {
  it("says how many steps the record dropped", () => {
    const note: MessagePart = { type: "data", id: "n", kind: "trace", data: { kind: "note", name: "truncated", omitted: 7, meta: { status: "ok", redaction: "omitted" } } };
    expect(html([step("s1", { status: "error" }), note])).toContain("7 steps were not kept");
  });
});

describe("in a message", () => {
  const message = (parts: MessagePart[]): ChatMessage => ({ id: "m", role: "assistant", parts, status: { state: "complete" }, createdAt: 0 });
  const text = (id: string): MessagePart => ({ type: "text", id, text: id });
  const render = (parts: MessagePart[], withRun: boolean) =>
    renderToStaticMarkup(
      <PartRegistryProvider renderers={{ text: ({ part }) => <p>{part.type === "text" ? part.text : ""}</p>, ...(withRun ? { run: createRunRenderer() } : {}) }}>
        <MessageContent message={message(parts)} />
      </PartRegistryProvider>,
    );

  it("draws adjacent steps as one run when a host registered `run`, with the text kept where it was", () => {
    const out = render([step("s1"), step("s2"), text("between"), step("s3"), step("s4")], true);
    expect(out.match(/class="chat-run"/g)).toHaveLength(2);
    expect(out.indexOf("Worked")).toBeLessThan(out.indexOf("between"));
  });

  // MUTANT: plan runs whether or not a renderer exists -> the default chat loses its tool cards.
  it("draws nothing of the kind without a `run` renderer (the fold stays as it was)", () => {
    expect(render([step("s1"), step("s2")], false)).not.toContain("chat-run");
    expect(planRuns([step("s1")])).toHaveLength(1);
  });
});
