/**
 * Mock payloads for the scenarios: typed constants, no secrets, no raw upstream artefacts.
 * Where a real server would redact, the redacted and the raw forms sit side by side so a privacy mode is visible.
 */

export interface Hit {
  readonly id: string;
  readonly title: string;
  readonly path: readonly string[];
  readonly excerpt: string;
}

/** Knowledge-base search hits. */
export const KB_HITS: readonly Hit[] = [
  { id: "kb-12", title: "Refund policy", path: ["Refund policy", "Eligibility"], excerpt: "Refunds are accepted within 14 days of payment when the service has not been used." },
  { id: "kb-31", title: "Onboarding a new client", path: ["Onboarding"], excerpt: "Every new client gets a kickoff call, a shared workspace and the checklist." },
  { id: "kb-40", title: "Holiday calendar", path: ["Company", "Calendar"], excerpt: "The office is closed on public holidays; support answers within one working day." },
];

export const KB_REFS = KB_HITS.map(({ id, title }) => ({ kind: "doc", id, title }));

/** An order lookup as the server returns it, and the view that may leave it. */
export const ORDER_RAW = { order: "A-1042", customer: "Alex Example", email: "alex@example.com", phone: "+1 555 0100", total: "48.00 USD", status: "shipped" } as const;
export const ORDER_MASKED = { order: "A-1042", customer: "A*** E*****", email: "a***@example.com", phone: "+1 *** ****", total: "48.00 USD", status: "shipped" } as const;

/** A long result, generated so nothing heavy is committed: a few thousand characters of rows, about 5 MB in its real size. */
export const longResult = (rows = 60): string =>
  Array.from({ length: rows }, (_, i) => `row ${String(i + 1).padStart(3, "0")}  order A-${1000 + i}  ${(i * 3.17 + 12).toFixed(2)} USD  shipped`).join("\n");

export const LONG_RESULT_BYTES = 5_242_880;

/** One very long unbroken word: the worst case for a bubble's width. */
export const LONG_WORD = "Pneumonoultramicroscopicsilicovolcanoconiosis".repeat(4);

export const WIDE_TABLE = [
  "| Region | Plan | Seats | Monthly | Annual | Notes |",
  "| --- | --- | --- | --- | --- | --- |",
  "| Europe | Team | 12 | 144 USD | 1 440 USD | Invoiced in euros |",
  "| North America | Business | 40 | 800 USD | 8 000 USD | Net 30 |",
  "| Asia | Team | 8 | 96 USD | 960 USD | Card only |",
].join("\n");

export const APPROVAL = {
  summary: "Store export dates as timestamps",
  changes: [
    { path: "export.created_at", from: "text", to: "timestamp" },
    { path: "export.updated_at", from: "text", to: "timestamp" },
    { path: "export.version", to: "2" },
  ],
} as const;

export const CHANGES = { title: "Updated the export schema", undoable: true, items: ["export.created_at", "export.updated_at", "export.finished_at"] } as const;

export const QUESTION = {
  question: "Which contact should I keep?",
  options: [{ label: "Katerina Gordeeva", description: "Added 2 March" }, { label: "Helen" }, { label: "Nika" }],
  other: "Someone else…",
} as const;

export const CITATIONS = { items: KB_HITS.map((hit, i) => ({ n: i + 1, title: hit.title, heading_path: hit.path })) } as const;

/** What a page-copilot proposal looks like on the wire: a `ui-action` card. */
export const ACTIONS = {
  fill: { id: "act-1", label: "Fill the Email field", action: { kind: "fill", ref: "@e2", value: "ada@example.com" } },
  click: { id: "act-2", label: "Press Save", action: { kind: "click", ref: "@e1" } },
} as const;
