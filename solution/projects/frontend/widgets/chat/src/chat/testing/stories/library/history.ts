import type { ChatMessage } from "../../../core/conversation/parts";
import { fromStoredThread } from "../../../../assistant/session";
import type { StoredThread } from "../../../../assistant/wire";
import { storedTurn, type Scenario } from "../scenario";
import { approval, sources } from "./blocks";

/** A picture an agent or a user could attach, drawn inline so nothing needs a network. */
const PICTURE = `data:image/svg+xml;utf8,${encodeURIComponent("<svg xmlns='http://www.w3.org/2000/svg' width='320' height='180'><rect width='320' height='180' fill='#0f172a'/><g fill='#6366f1'><rect x='30' y='90' width='40' height='60'/><rect x='90' y='60' width='40' height='90'/><rect x='150' y='30' width='40' height='120'/><rect x='210' y='50' width='40' height='100'/></g></svg>")}`;

const at = Date.UTC(2026, 10, 10, 9, 0, 0);

const user = (id: string, text: string, files: ChatMessage["parts"] = []): ChatMessage => ({ id, role: "user", parts: [...files, { type: "text", id: `${id}:t`, text }], status: { state: "complete" }, createdAt: at });
const bot = (id: string, text: string): ChatMessage => ({ id, role: "assistant", parts: [{ type: "text", id: `${id}:t`, text }], status: { state: "complete" }, createdAt: at + 1000 });

/** A session reloaded from the server: what a stored turn restores (the steps first, then the words and the cards). */
export const restoredSession: Scenario = {
  id: "restored-session",
  title: "A restored session",
  note: "Reopened from the server: each answer keeps its steps and its cards. A thread never shows a spinner without a stream behind it.",
  group: "history",
  prompt: "",
  messageId: "restored",
  beats: [],
  seed: 1,
  history: fromStoredThread([...storedTurn(sources), ...storedTurn(approval)], "Something went wrong. Try again."),
};

/** Files on a user message: a picture that opens large, a file, and one whose bytes the server deleted. */
export const attachments: Scenario = {
  id: "attachments",
  title: "Attachments in a conversation",
  note: "A picture (click it), a file link, and a file the server no longer holds: a muted chip, never a broken link.",
  group: "attachments",
  prompt: "",
  messageId: "attachments",
  beats: [],
  seed: 1,
  history: [
    user("a1", "Here is the chart and last week's summary.", [
      { type: "attachment", id: "a1:1", attachment: { id: "f1", name: "tasks-per-day.svg", mime: "image/svg+xml", size: 1_204, kind: "image", url: PICTURE } },
      { type: "attachment", id: "a1:2", attachment: { id: "f2", name: "weekly-summary.pdf", mime: "application/pdf", size: 188_416, kind: "document", url: "#" } },
      { type: "attachment", id: "a1:3", attachment: { id: "f3", name: "old-export.csv", mime: "text/csv", size: 4_200_000, kind: "text", url: "" } },
    ]),
    bot("a2", "I can see the chart and the summary. The old export has expired, so I could not read it."),
  ],
};

export const SESSION_ROWS: readonly StoredThread[] = [
  { id: "t1", title: "What is our refund policy?", last_message_at: "2026-11-10T08:30:00Z", message_count: 4 },
  { id: "t2", title: "Store the export dates as timestamps", last_message_at: "2026-11-10T07:10:00Z", message_count: 6 },
  { id: "t3", title: "Where is my order A-1042?", last_message_at: "2026-11-09T16:00:00Z", message_count: 2 },
  { id: "t4", title: "Weekly overview", last_message_at: "2026-10-28T11:00:00Z", message_count: 8 },
];
