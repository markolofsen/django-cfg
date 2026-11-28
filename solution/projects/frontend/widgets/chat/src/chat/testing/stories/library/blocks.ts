import { scenario } from "../scenario";
import { ACTIONS, APPROVAL, CHANGES, CITATIONS, KB_REFS, QUESTION } from "./payloads";

export const question = scenario({ id: "question", title: "A question with options", note: "The agent needs one answer. A pick is sent as your next message, then the card locks.", group: "blocks", prompt: "Merge the duplicate contacts." })
  .say("Before I change anything I need one answer.\n")
  .payload("ask", QUESTION)
  .finish()
  .build();

export const approval = scenario({ id: "approval", title: "Approve a change", note: "Apply and Dismiss reply as your next message. After a finished change, Undo.", group: "blocks", prompt: "Store the export dates as timestamps." })
  .tool("schema_diff", { label: "Comparing the schemas", summary: "3 columns differ", ms: 800, args: { table: "export" } })
  .say("I prepared the change. Nothing is applied until you press Apply.\n")
  .payload("approval", APPROVAL)
  .payload("changes", CHANGES)
  .finish()
  .build();

export const sources = scenario({ id: "sources", title: "An answer with sources", note: "Citation chips under the answer, and the documents each step touched.", group: "blocks", prompt: "What is our refund policy?" })
  .tool("kb_search", { label: "Searching the knowledge base", summary: "3 passages", ms: 700, refs: KB_REFS, args: { query: "refund" } })
  .say("A client can ask for a refund within 14 days of paying [1]. Onboarding follows the checklist [2].\n")
  .payload("citations", CITATIONS)
  .finish()
  .build();

export const pageCopilot = scenario({ id: "page-copilot", title: "The agent proposes page actions", note: "It points at the field it means; nothing happens until you agree.", group: "blocks", prompt: "Fill in my email and save." })
  .say("I can fill in your email and press Save. Check each step first.\n")
  .payload("ui-action", ACTIONS.fill)
  .payload("ui-action", ACTIONS.click)
  .finish()
  .build();
