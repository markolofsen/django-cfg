import type { ChatMessage } from "../../../core/conversation/parts";

/**
 * The scripted scenario model.
 *
 * A scenario is a list of timed BEATS in one neutral vocabulary (what an answer does, not how a
 * transport spells it). `compile.ts` turns it into the chunk stream a mock adapter replays AND the
 * frame stream the assistant's scripted transport replays, so one scenario drives both paths and
 * `parity.test.ts` proves they build the same transcript.
 *
 * Authored as the server would send it: a step is the raw v1 wire step, so the shipped decoder
 * (`decodeStep`) and mapping (`stepPart`) decide what is drawn, not a posed object.
 */

/** A `TraceStep` v1 as JSON, before the decoder reads it. */
export type RawStep = Readonly<Record<string, unknown>>;

export type StreamErrorCode = "unavailable" | "timeout" | "failed";

/** Where a beat sits, in milliseconds from the start of the run. Absolute, so parallel calls interleave truthfully. */
interface Timed {
  readonly at: number;
}

export type Beat =
  /** Words arriving one token at a time over `ms`. Consecutive `say` beats continue one text part. */
  | (Timed & { readonly kind: "say"; readonly text: string; readonly ms: number })
  /** A live thought (`reasoning_delta` text) that ends with its measured time and tokens. */
  | (Timed & { readonly kind: "think"; readonly text: string; readonly ms: number; readonly tokens?: number })
  /** One trace step frame. A step is sent twice (running, then settled) under the same `step_id`. */
  | (Timed & { readonly kind: "step"; readonly step: RawStep; readonly eventSeq: number })
  /** A structured card, by the same `kind` a live `ui_payload` carries. */
  | (Timed & { readonly kind: "payload"; readonly name: string; readonly data: unknown })
  | (Timed & { readonly kind: "finish" })
  /** The server reported the turn as failed. */
  | (Timed & { readonly kind: "fail"; readonly code: StreamErrorCode; readonly message: string })
  /** The transport died without a terminal frame (a lost stream). */
  | (Timed & { readonly kind: "lost" })
  /** No answer at all: the request never reached a server. */
  | (Timed & { readonly kind: "offline" });

export type BeatKind = Beat["kind"];

/** Which area of the chat a scenario shows, in the order the overview lists them. */
export type ScenarioGroup =
  | "messages"
  | "run"
  | "tools"
  | "blocks"
  | "failures"
  | "history"
  | "attachments"
  | "privacy";

export interface Scenario {
  readonly id: string;
  /** A user-visible state, not a technical case name. */
  readonly title: string;
  /** One sentence: what to look at. */
  readonly note: string;
  readonly group: ScenarioGroup;
  /** What the user types to start the turn. */
  readonly prompt: string;
  readonly messageId: string;
  readonly beats: readonly Beat[];
  /** Messages already in the thread before the turn (a restored session). */
  readonly history?: readonly ChatMessage[];
  /** Run options a scenario needs to be read as intended (a public chat, a compact run). */
  readonly seed: number;
}

/** A fixed clock: the core reads none, and fixtures must be deterministic. */
export const FIXED_NOW = Date.UTC(2026, 10, 10, 9, 0, 0);

/** mulberry32: a tiny seeded generator. Same seed, same run. */
export function rng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Split prose into token-sized pieces that keep their whitespace, so joining them returns the text. */
export function tokens(text: string): string[] {
  return text.split(/(?<=\s)/).filter((piece) => piece !== "");
}
