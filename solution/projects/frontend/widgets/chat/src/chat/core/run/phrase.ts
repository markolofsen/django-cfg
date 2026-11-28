/**
 * A step as a short sentence: "Read Sales", "Searched Projects", "Thinking…".
 *
 * Headless. The words come from the host's map, then the server's own `label`; only
 * when neither exists does a template by kind of work speak ("Read {{object}}"), with
 * the thing it touched as its object. A server label is the whole sentence; the
 * object is a separate span only in a template, so the UI can set it apart.
 */

import { readableToolName } from "../tools/name";
import type { RunStep } from "./view";

/** The sentence, split around its object: `before + object + after`. Without an object `after` is empty. */
export interface StepPhrase {
  readonly before: string;
  readonly object?: string;
  readonly after: string;
  /** The object is a title the server gave (a source), not the tool's own name. */
  readonly named: boolean;
}

/** The kind of work a step did. The dictionary (`i18n`, which imports nothing) keeps the same five names, and the UI checks they agree by type. */
export type RunVerbWord = "read" | "search" | "write" | "other" | "think";

const READ = new Set(["read", "get", "fetch", "open", "load", "view", "retrieve", "download", "inspect", "peek"]);
const SEARCH = new Set(["search", "find", "query", "lookup", "list", "grep", "browse", "scan", "ask"]);
const WRITE = new Set(["write", "create", "update", "edit", "save", "send", "delete", "add", "set", "remove", "post", "put", "insert", "upload", "patch", "append", "draft"]);

const words = (name: string): string[] =>
  readableToolName(name)
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(Boolean);

/** The kind of work a step did: what a template should call it. */
export function stepVerb(step: RunStep): RunVerbWord {
  if (step.kind === "reasoning") return "think";
  const role = step.meta.role;
  if (role === "read") return "read";
  if (role === "retriever" || role === "search") return "search";
  if (role === "write" || role === "propose") return "write";
  for (const word of step.name === undefined ? [] : words(step.name)) {
    if (READ.has(word)) return "read";
    if (SEARCH.has(word)) return "search";
    if (WRITE.has(word)) return "write";
  }
  return "other";
}

const MARK = "{{object}}";

export interface PhraseWords {
  readonly verb: Readonly<Record<RunVerbWord, { readonly done: string; readonly live: string }>>;
  /** The generic word for a step kind that is not a tool or a thought (`Model`, `Usage`, ...). */
  readonly kind: (kind: string) => string;
}

/**
 * `labels` is the host's map by tool name. `object` is what the step touched when the
 * server named it (the first source's title); without it a tool's readable name stands.
 */
export function stepPhrase(step: RunStep, words_: PhraseWords, labels: Readonly<Record<string, string>> | undefined, object: string | undefined): StepPhrase {
  const live = step.status === "running" || step.status === "pending";
  const mapped = step.name === undefined ? undefined : labels?.[step.name];
  if (mapped !== undefined && mapped !== "") return { before: mapped, after: "", named: false };
  const { label, summary } = step.meta;
  if (label !== undefined && label !== "") return { before: label, after: "", named: false };
  if (step.kind === "reasoning") {
    // A thought's summary IS its sentence ("Considering user needs for visuals").
    if (summary !== undefined && summary !== "") return { before: summary, after: "", named: false };
    const think = words_.verb.think;
    return { before: live ? think.live : think.done, after: "", named: false };
  }
  if (step.kind !== "tool") return { before: words_.kind(step.kind), after: "", named: false };
  const template = words_.verb[stepVerb(step)][live ? "live" : "done"];
  const target = object ?? (step.name === undefined ? undefined : readableToolName(step.name));
  const at = template.indexOf(MARK);
  if (target === undefined || at < 0) return { before: template.replace(MARK, "").trim(), after: "", named: false };
  return { before: template.slice(0, at), object: target, after: template.slice(at + MARK.length), named: object !== undefined };
}

/** The phrase as one string (a live line, an accessible name, an export). */
export const phraseText = (p: StepPhrase): string => `${p.before}${p.object ?? ""}${p.after}`.trim();
