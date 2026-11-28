/**
 * The payloads of the interactive blocks, one parser each.
 *
 * Each takes `unknown` and returns `null` for a malformed payload, so the renderer draws nothing rather than a broken card (the rule of `ui/renderers/data.tsx`).
 * These shapes are the wire contract a backend emits as a `data` part with the matching `kind`.
 */

import { BLOCK_KINDS } from "../core";

export { BLOCK_KINDS };
export type BlockKind = (typeof BLOCK_KINDS)[number];

export interface AskOption {
  /** What is sent back as the answer. */
  readonly label: string;
  readonly description?: string;
}

/** A question the agent needs answered: pick one option, and/or type a free answer. */
export interface AskPayload {
  readonly question?: string;
  readonly options: readonly AskOption[];
  /** Allow a typed answer beside the options. A string is the field's placeholder. Always on when there are no options. */
  readonly other: boolean | string;
}

export interface ApprovalChange {
  readonly path: string;
  readonly from?: string;
  readonly to: string;
}

/** A proposed change that waits for Apply. */
export interface ApprovalPayload {
  readonly summary: string;
  readonly changes: readonly ApprovalChange[];
}

export interface ChangedItem {
  readonly label: string;
  readonly href?: string;
}

/** A change that already happened: what it was and what it touched. */
export interface ChangesPayload {
  readonly title: string;
  readonly items: readonly ChangedItem[];
  /** Show an Undo button. Which action it takes is the host's (`onAnswer`), or a message by default. */
  readonly undoable: boolean;
}

const isObject = (value: unknown): value is Record<string, unknown> => typeof value === "object" && value !== null;
const text = (value: unknown): string | undefined => (typeof value === "string" && value.trim() !== "" ? value : undefined);

export function readAsk(data: unknown): AskPayload | null {
  if (!isObject(data)) return null;
  const options: AskOption[] = [];
  for (const raw of Array.isArray(data.options) ? data.options : []) {
    const label = typeof raw === "string" ? text(raw) : isObject(raw) ? text(raw.label) : undefined;
    if (label === undefined) continue;
    const description = isObject(raw) ? text(raw.description) : undefined;
    options.push({ label, ...(description ? { description } : {}) });
  }
  const other = typeof data.other === "string" ? data.other : data.other === true;
  const question = text(data.question);
  if (options.length === 0 && other === false && question === undefined) return null;
  return { ...(question ? { question } : {}), options, other: options.length === 0 ? other || true : other };
}

export function readApproval(data: unknown): ApprovalPayload | null {
  if (!isObject(data)) return null;
  const summary = text(data.summary);
  if (summary === undefined) return null;
  const changes: ApprovalChange[] = [];
  for (const raw of Array.isArray(data.changes) ? data.changes : []) {
    if (!isObject(raw)) continue;
    const path = text(raw.path);
    const to = text(raw.to);
    if (path === undefined || to === undefined) continue;
    const from = text(raw.from);
    changes.push({ path, to, ...(from ? { from } : {}) });
  }
  return { summary, changes };
}

/** http(s) and same-origin paths only: an item link is a URL the model chose. */
function safeHref(value: unknown): string | undefined {
  const url = text(value);
  if (url === undefined) return undefined;
  if (url.startsWith("/") && !url.startsWith("//")) return url;
  try {
    return ["http:", "https:"].includes(new URL(url).protocol) ? url : undefined;
  } catch {
    return undefined;
  }
}

export function readChanges(data: unknown): ChangesPayload | null {
  if (!isObject(data)) return null;
  const title = text(data.title);
  if (title === undefined) return null;
  const items: ChangedItem[] = [];
  for (const raw of Array.isArray(data.items) ? data.items : []) {
    const label = typeof raw === "string" ? text(raw) : isObject(raw) ? text(raw.label) : undefined;
    if (label === undefined) continue;
    const href = isObject(raw) ? safeHref(raw.href) : undefined;
    items.push({ label, ...(href ? { href } : {}) });
  }
  return { title, items, undoable: isObject(data) && data.undoable === true };
}

/**
 * What an approval or an undo says to the agent. Fixed English, not the UI language: the reply is for the agent's prompt, which a host writes once (`Apply: <summary>`),
 * and a reader's locale must not change what the agent is asked to recognise. The buttons and the confirmations on screen are translated; this is not.
 */
export const BLOCK_REPLY = { apply: "Apply", dismiss: "Dismiss", undo: "Undo" } as const;
