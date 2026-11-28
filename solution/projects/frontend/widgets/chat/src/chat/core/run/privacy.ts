/**
 * What the Run block may show of a step, decided on the client as a second lock.
 *
 * The server already redacted: `meta.redaction` says how, and the decoder dropped
 * everything an `omitted` step carried. This only NARROWS that. It never widens
 * it, and it never stands in for it (a client-side mask is not a secret filter:
 * the server's view is the contract). Fail closed throughout: a step with no
 * `redaction` mark, an unknown mode or a mask pattern that does not compile shows
 * less, never more.
 */

import type { RunStep } from "./view";
import type { StepRef, StepTokens } from "../conversation/parts";

export type ArgsMode = "hidden" | "keys" | "masked" | "full";
export type ResultMode = "hidden" | "preview" | "full";

export interface RunPrivacyOptions {
  /** Arguments: nothing, the names only (default), values with `maskPatterns` applied, or values as the server sent them (`maskPatterns` still apply). */
  readonly argsMode?: ArgsMode;
  /** The result: nothing, a short preview (default) or the whole view the server sent. */
  readonly resultMode?: ResultMode;
  /** Applied to every shown value and to the result; a match is replaced by `•••`. Strings are regular expressions (case-insensitive). */
  readonly maskPatterns?: readonly (string | RegExp)[];
  /** The preview's length. Default 280. */
  readonly maxPreviewChars?: number;
  /** A public chat: titles, statuses and the server's one-line summaries only. No arguments, results, purpose, query, sources or thought text. */
  readonly labelsOnly?: boolean;
  /** Show the words of a live thought (a tail while it streams, the text once settled). Default false: a thought is counted, not read. */
  readonly showReasoningText?: boolean;
}

export interface ResolvedPrivacy {
  readonly argsMode: ArgsMode;
  readonly resultMode: ResultMode;
  readonly masks: readonly RegExp[];
  readonly maxPreviewChars: number;
  readonly labelsOnly: boolean;
  readonly showReasoningText: boolean;
}

const ARGS_MODES: readonly string[] = ["hidden", "keys", "masked", "full"];
const RESULT_MODES: readonly string[] = ["hidden", "preview", "full"];
export const MASK = "•••";

export function resolvePrivacy(options: RunPrivacyOptions = {}): ResolvedPrivacy {
  const masks: RegExp[] = [];
  let broken = false;
  for (const pattern of options.maskPatterns ?? []) {
    try {
      masks.push(typeof pattern === "string" ? new RegExp(pattern, "gi") : new RegExp(pattern.source, pattern.flags.includes("g") ? pattern.flags : `${pattern.flags}g`));
    } catch {
      broken = true;
    }
  }
  const labelsOnly = options.labelsOnly === true;
  // A pattern that cannot be applied means a value cannot be masked, so none is shown.
  const argsMode: ArgsMode = labelsOnly || broken ? "hidden" : ARGS_MODES.includes(options.argsMode ?? "") ? (options.argsMode as ArgsMode) : "keys";
  const resultMode: ResultMode = labelsOnly || broken ? "hidden" : RESULT_MODES.includes(options.resultMode ?? "") ? (options.resultMode as ResultMode) : "preview";
  return {
    argsMode,
    resultMode,
    masks,
    maxPreviewChars: Math.max(20, options.maxPreviewChars ?? 280),
    labelsOnly,
    showReasoningText: !labelsOnly && options.showReasoningText === true,
  };
}

function mask(text: string, masks: readonly RegExp[]): string {
  return masks.reduce((out, re) => out.replace(re, MASK), text);
}

function valueText(value: unknown): string {
  if (typeof value === "string") return value;
  if (value === null || typeof value !== "object") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return MASK;
  }
}

const clip = (text: string, max: number): string => (text.length > max ? `${text.slice(0, max)}…` : text);

/** What the server allowed the detail to carry: a `none` or `masked` mark. Anything else (absent, `omitted`, unknown) is closed. */
const serverAllows = (step: RunStep): boolean => step.meta.redaction === "none" || step.meta.redaction === "masked";

export interface StepDetail {
  readonly purpose?: string;
  readonly query?: string;
  /** Argument names with their values, when the mode shows them (else just names). */
  readonly args?: readonly { readonly key: string; readonly value?: string }[];
  readonly result?: string;
  readonly resultClipped?: boolean;
  readonly sources?: readonly StepRef[];
  readonly tokens?: StepTokens;
  readonly costUsd?: number;
  readonly model?: string;
  readonly errorCode?: string;
  readonly retryable?: boolean;
  /** The server held its details back for this step (say so, rather than show an empty box). */
  readonly notShared: boolean;
  /** The server masked some values. */
  readonly masked: boolean;
  /** The server shortened the result. */
  readonly truncated: boolean;
}

export const NO_DETAIL: StepDetail = { notShared: false, masked: false, truncated: false };

/** What a step's disclosure shows, under the privacy in force. */
export function detailOf(step: RunStep, privacy: ResolvedPrivacy): StepDetail {
  if (privacy.labelsOnly) return NO_DETAIL;
  const { meta } = step;
  const allowed = serverAllows(step);
  const base = {
    ...(meta.tokens === undefined ? {} : { tokens: meta.tokens }),
    ...(meta.costUsd === undefined ? {} : { costUsd: meta.costUsd }),
    ...(meta.model === undefined ? {} : { model: meta.model }),
    ...(meta.errorCode === undefined ? {} : { errorCode: meta.errorCode }),
    ...(meta.retryable === undefined ? {} : { retryable: meta.retryable }),
  };
  if (!allowed) return { ...base, notShared: meta.redaction === "omitted", masked: false, truncated: false };

  const { masks } = privacy;
  const args =
    privacy.argsMode === "hidden" || meta.argsView === undefined
      ? undefined
      : Object.entries(meta.argsView).map(([key, value]) => (privacy.argsMode === "keys" ? { key } : { key, value: clip(mask(valueText(value), masks), 400) }));
  const raw = privacy.resultMode === "hidden" ? undefined : meta.resultView;
  const result = raw === undefined ? undefined : mask(privacy.resultMode === "preview" ? clip(raw, privacy.maxPreviewChars) : raw, masks);
  return {
    ...base,
    ...(meta.purpose === undefined ? {} : { purpose: mask(meta.purpose, masks) }),
    ...(meta.query === undefined ? {} : { query: mask(meta.query, masks) }),
    ...(args === undefined || args.length === 0 ? {} : { args }),
    ...(result === undefined ? {} : { result, resultClipped: privacy.resultMode === "preview" && raw !== undefined && raw.length > privacy.maxPreviewChars }),
    ...(meta.sources === undefined || meta.sources.length === 0 ? {} : { sources: meta.sources }),
    notShared: false,
    masked: meta.redaction === "masked",
    truncated: meta.truncated === true,
  };
}

/** Whether a disclosure has anything to open. */
export function hasDetail(detail: StepDetail): boolean {
  return (
    detail.notShared ||
    detail.purpose !== undefined ||
    detail.query !== undefined ||
    detail.args !== undefined ||
    detail.result !== undefined ||
    detail.sources !== undefined ||
    detail.tokens !== undefined ||
    detail.costUsd !== undefined ||
    detail.errorCode !== undefined
  );
}

/** The words of a thought, when the host allows them: the whole text, or only its last `tail` characters. */
export function thoughtText(step: RunStep, privacy: ResolvedPrivacy, tail?: number): string | undefined {
  if (!privacy.showReasoningText || step.part.type !== "reasoning" || step.part.text === "") return undefined;
  const text = mask(step.part.text, privacy.masks);
  return tail !== undefined && text.length > tail ? `…${text.slice(-tail)}` : text;
}
