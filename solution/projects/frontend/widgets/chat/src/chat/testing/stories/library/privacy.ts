import { scenario } from "../scenario";
import { ORDER_MASKED, ORDER_RAW } from "./payloads";

/**
 * One run, two readers. The server decides what leaves it (`redaction`); the host decides how much of that the screen shows
 * (`argsMode`, `resultMode`, `labelsOnly`). The story draws this scenario twice: a visitor on a public chat and a signed-in admin.
 */
export const privacy = scenario({ id: "privacy", title: "Public and admin, side by side", note: "The same run: a visitor sees titles and statuses; an admin sees arguments and results.", group: "privacy", prompt: "Where is my order A-1042?" })
  .tool("order_lookup", { label: "Looking up the order", summary: "Shipped", purpose: "Find the order the customer named", redaction: "masked", args: { order: "A-1042", email: "a***@example.com" }, argsSize: 64, ms: 600, result: { preview: JSON.stringify(ORDER_MASKED), size: JSON.stringify(ORDER_RAW).length } })
  .tool("internal_notes", { label: "Reading internal notes", summary: "1 note", redaction: "omitted", args: { order: "A-1042" }, ms: 300, result: { preview: "never shown", size: 90 } })
  .tool("kb_search", { label: "Searching the knowledge base", summary: "2 passages", query: "delivery times", args: { query: "delivery times" }, ms: 500, result: { preview: "Parcels ship within one working day.", size: 120 } })
  .say("Your order A-1042 has shipped.\n")
  .finish()
  .build();
