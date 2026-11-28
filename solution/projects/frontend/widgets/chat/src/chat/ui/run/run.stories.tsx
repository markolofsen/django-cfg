import type { Meta, StoryObj } from "@storybook/react-vite";

import type { MessagePart, RunPart } from "../../core/conversation/parts";
import { RunBlock } from "./block";
import { step } from "./stories/steps";

/**
 * What an answer did, drawn from real trace steps (the shipped decoder and mapping, not
 * posed objects): the default quiet look (Notion-like), a live line, a settled "Worked for
 * 10s", a failed step that opens itself, the full timeline with a disclosure per step, a
 * public chat that shows labels only, and a run past one page.
 */
const run = (parts: MessagePart[]): RunPart => ({ type: "run", id: "run", parts });

const searching = step("s1", { label: "Searching the knowledge base", summary: "4 passages", started_ms: 0, duration_ms: 900, args: { query: "refund window", limit: 5 }, args_size: 40, result: { preview: "Refunds are accepted within 30 days of delivery.", size: 48 }, purpose: "Find the refund policy", refs: [{ kind: "doc", id: "kb-12", title: "Refund policy" }] });
const reading = step("s2", { label: "Reading the policy page", started_ms: 900, duration_ms: 400, redaction: "masked", args: { url: "https://shop.example/policy" }, result: { preview: "Items may be returned unused…", size: 900, truncated: true } });
const thinking = step("s3", { kind: "reasoning", name: "reasoning", started_ms: 1300, duration_ms: 1500, tokens: { reasoning: 220 } });
const lookup = step("s4", { label: "Looking up the order", status: "timeout", started_ms: 2800, duration_ms: 30000, summary: "The order service did not answer", error: { code: "timeout", retryable: true }, args: { order: "A-1042" } });
const usage = step("s5", { kind: "usage", name: "usage", label: "Usage", started_ms: 32800, duration_ms: 0, model: "gpt-4o-mini", tokens: { input: 1200, output: 340 }, cost_usd: 0.0012 });

const considering: MessagePart = {
  type: "reasoning",
  id: "r1",
  text: "The user wants a diagram rather than just a data chart. They seem interested in a visual artifact, potentially generated with Mermaid. Mermaid is native to the page editor, so it could display diagrams well. I should confirm this approach works best, then check the official resources for details on using Mermaid there. Let me make sure I am clear on the requirements before I change anything.",
  streaming: false,
  meta: { status: "ok", summary: "Considering user needs for visuals", redaction: "none", durationMs: 2100 },
};
const notion: MessagePart[] = [
  step("n1", { name: "read_page", started_ms: 0, duration_ms: 2000, refs: [{ kind: "page", id: "p1", title: "Sales" }] }),
  step("n2", { name: "read_page", started_ms: 2000, duration_ms: 1200, refs: [{ kind: "page", id: "p2", title: "CRM overview" }] }),
  step("n3", { name: "search_pages", started_ms: 3200, duration_ms: 900, summary: "12 results" }),
  step("n4", { name: "search_pages", label: "Searched how to render a Mermaid diagram", started_ms: 4100, duration_ms: 700 }),
  considering,
  step("n5", { name: "write_page", started_ms: 6000, duration_ms: 800, refs: [{ kind: "page", id: "p3", title: "Overview" }] }),
];

const meta = {
  title: "Widgets/Chat/Run",
  component: RunBlock,
  args: { run: run([searching]) },
  parameters: { layout: "padded", a11y: { test: "error" } },
  decorators: [(Story) => <div style={{ maxInlineSize: "34rem" }}><Story /></div>],
} satisfies Meta<typeof RunBlock>;

export default meta;
type Story = StoryObj<typeof meta>;

/** The default: "Worked for 10s", and a flat list of one-line steps under a thin rule. No card, no status column; the thought opens to its words. */
export const NotionLike: Story = { args: { run: run(notion), options: { defaultOpen: true, showReasoningText: true } } };

/** One line while it works: the live step in the server's words, and a counter. */
export const Running: Story = { args: { run: run([searching, step("s2", { label: "Reading 3 emails", status: "running" })]) } };

/** Settled and quiet: "Worked for 10s", closed. */
export const Settled: Story = { args: { run: run([searching, reading, thinking, usage]) } };

/** A failed step opens the block by itself and stays open; the others stay one line each. */
export const Failed: Story = { args: { run: run([searching, reading, lookup]) } };

/** The whole timeline with a disclosure per step: arguments, result, why, sources, tokens. */
export const Timeline: Story = { args: { run: run([searching, reading, thinking, lookup, usage]), options: { defaultOpen: true, argsMode: "full", resultMode: "full", maskPatterns: ["https?://\\S+"] } } };

/** A live thought: a bounded box that follows the stream, faded at the top, and only because the host allowed its words. */
export const ThoughtTail: Story = {
  args: {
    run: run([searching, { type: "reasoning", id: "r", text: "The customer asks about a return. ".repeat(20), streaming: true, meta: { status: "running", redaction: "none" } }]),
    options: { defaultOpen: true, showReasoningText: true },
  },
};

/** A public chat: titles, statuses and the one-line summaries. Nothing else leaves the block. */
export const LabelsOnly: Story = { args: { run: run([searching, reading, lookup]), options: { labelsOnly: true } } };

/** Past a page: 25 at a time, and the failed step is never behind "Show more". */
export const LongRun: Story = {
  args: {
    run: run([...Array.from({ length: 70 }, (_, i) => step(`s${i + 1}`, { label: `Step ${i + 1}`, duration_ms: 120 })), step("s71", { label: "A late failure", status: "error", summary: "Pinned open" })]),
    options: { defaultOpen: true },
  },
};

/** The stored record dropped steps (its own cap): the block says how many. */
export const Truncated: Story = {
  args: { run: run([searching, reading, { type: "data", id: "n", kind: "trace", data: { kind: "note", name: "truncated", omitted: 12, meta: { status: "ok", redaction: "omitted" } } }]), options: { defaultOpen: true } },
};
