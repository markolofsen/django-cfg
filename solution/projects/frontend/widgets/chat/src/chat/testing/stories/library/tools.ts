import { scenario } from "../scenario";
import { KB_HITS, KB_REFS, LONG_RESULT_BYTES, longResult } from "./payloads";

const ANSWER = "A client can ask for a refund within 14 days of paying [1]. Onboarding follows the checklist [2]. ";

export const reasoning = scenario({ id: "reasoning", title: "Thinking, then answering", note: "A live thought that settles into 'Thought for N s', then the answer.", group: "run", prompt: "What is our refund policy?" })
  .think("The customer asks about refunds. I should check the policy page for the window and the conditions before I answer. ", { tokens: 64 })
  .say("Refunds are accepted within 14 days of payment, as long as the service has not been used.\n")
  .finish()
  .build();

export const hiddenThought = scenario({ id: "hidden-thought", title: "Thought with no words", note: "The provider kept the words. Only the time and the tokens are true, so only those are shown.", group: "run", prompt: "What is our refund policy?" })
  .step({ v: 1, step_id: "s1", seq: 1, kind: "reasoning", name: "reasoning", status: "running", redaction: "none", started_ms: 120 }, 120)
  .wait(1800)
  .step({ v: 1, step_id: "s1", seq: 1, kind: "reasoning", name: "reasoning", status: "ok", redaction: "none", started_ms: 120, duration_ms: 1800, tokens: { reasoning: 220 } })
  .say("Refunds are accepted within 14 days of payment.\n")
  .finish()
  .build();

export const toolRun = scenario({ id: "tool-run", title: "A tool run with sources", note: "Search, read, a short thought, a usage line, then the answer with its sources.", group: "tools", prompt: "What is our refund policy?" })
  .tool("kb_search", { label: "Searching the knowledge base", summary: "3 passages", purpose: "Find the refund policy", query: "refund window", args: { query: "refund window", limit: 3 }, argsSize: 38, ms: 900, result: { preview: KB_HITS[0]?.excerpt ?? "", size: 420 }, refs: KB_REFS })
  .tool("kb_read", { label: "Reading the policy page", summary: "1 page", args: { id: "kb-12" }, ms: 400, result: { preview: "Items may be returned unused within 14 days…", size: 900 } })
  .think("The page states the window and one condition. ", { tokens: 40, ms: 800 })
  .tool("usage", { kind: "usage", label: "Usage", ms: 0, tokens: { input: 1200, output: 340 }, costUsd: 0.0012 })
  .say(ANSWER)
  .finish()
  .build();

export const toolError = scenario({ id: "tool-error", title: "A call failed", note: "The failed row opens itself and stays open; the answer still arrives.", group: "tools", prompt: "Where is my order A-1042?" })
  .tool("order_lookup", { label: "Looking up the order", status: "error", summary: "The order service refused the request", error: { code: "upstream_5xx", retryable: true }, args: { order: "A-1042" }, ms: 700 })
  .say("I could not reach the order service, so I cannot confirm the status yet. Please try again in a minute.\n")
  .finish()
  .build();

export const toolTimeout = scenario({ id: "tool-timeout", title: "A call timed out", note: "Timeout is its own status, with the server's words.", group: "tools", prompt: "Where is my order A-1042?" })
  .tool("order_lookup", { label: "Looking up the order", status: "timeout", summary: "The order service did not answer in time", error: { code: "timeout", retryable: true }, args: { order: "A-1042" }, ms: 30_000 })
  .say("The order service did not answer. You can ask me to try again.\n")
  .finish()
  .build();

/** A call still open when the stream ends: the turn is interrupted and the call is closed as stopped, never as failed. */
export const toolCancelled = scenario({ id: "tool-cancelled", title: "Stopped mid-call", note: "The stream ended while a call ran. The row says Stopped, not Failed.", group: "tools", prompt: "Summarise the open orders." })
  .step({ v: 1, step_id: "s1", seq: 1, kind: "tool", name: "order_search", status: "running", redaction: "none", label: "Searching open orders", started_ms: 120, args: { status: "open" } }, 120)
  .wait(900)
  .lost()
  .build();

export const parallelBatch = scenario({ id: "parallel-batch", title: "Four calls at once", note: "Calls that start together finish on their own clocks.", group: "tools", prompt: "Compare the four regions." })
  .parallel([
    ["region_stats", { label: "Europe", summary: "12 teams", ms: 600, args: { region: "eu" } }],
    ["region_stats", { label: "North America", summary: "40 teams", ms: 1500, args: { region: "na" } }],
    ["region_stats", { label: "Asia", summary: "8 teams", ms: 900, args: { region: "as" } }],
    ["region_stats", { label: "Africa", summary: "no data", status: "skipped", ms: 200, args: { region: "af" } }],
  ])
  .say("North America is the largest region. Africa has no data yet.\n")
  .finish()
  .build();

export const retryChain = scenario({ id: "retry-chain", title: "Three attempts", note: "Two failures that said they could be retried, then success. Each attempt is a row.", group: "tools", prompt: "Fetch the exchange rate." })
  .tool("rates_api", { label: "Fetching the rate (attempt 1 of 3)", status: "error", summary: "Rate limited", error: { code: "rate_limited", retryable: true }, ms: 300 })
  .tool("rates_api", { label: "Fetching the rate (attempt 2 of 3)", status: "error", summary: "Rate limited", error: { code: "rate_limited", retryable: true }, ms: 300 })
  .tool("rates_api", { label: "Fetching the rate (attempt 3 of 3)", summary: "1 USD = 0.92 EUR", ms: 500, result: { preview: "1 USD = 0.92 EUR", size: 16 } })
  .say("1 USD is 0.92 EUR right now.\n")
  .finish()
  .build();

const longRun = scenario({ id: "long-run", title: "A run of sixty steps", note: "Past one page the run shows 25 at a time; the last step failed and is never behind 'Show more'.", group: "tools", prompt: "Audit every export.", seed: 11 });
for (let i = 1; i <= 59; i += 1) longRun.tool("audit_export", { label: `Checking export ${i}`, summary: "ok", ms: 90 + ((i * 37) % 160), args: { export: i } });
longRun.tool("audit_export", { label: "Checking export 60", status: "error", summary: "The file is corrupt", error: { code: "corrupt", retryable: false }, ms: 200, args: { export: 60 } });
export const longRunScenario = longRun.say("59 exports are fine. Export 60 is corrupt.\n").finish().build();

export const longResultScenario = scenario({ id: "long-result", title: "A very long result", note: "The step keeps a preview and says how large the rest is. The detail never holds megabytes.", group: "tools", prompt: "Export all orders." })
  .tool("orders_export", { label: "Exporting orders", summary: "5 MB", ms: 1200, args: { format: "csv" }, argsSize: 16, result: { preview: longResult(), size: LONG_RESULT_BYTES, truncated: true } })
  .say("The export is ready. Only a preview is shown here.\n")
  .finish()
  .build();
