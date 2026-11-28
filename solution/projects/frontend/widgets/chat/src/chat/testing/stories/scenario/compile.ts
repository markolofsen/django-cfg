import type { StreamChunk } from "../../../core/conversation/chunks";
import { decodeFrame, StreamLostError, type Frame } from "../../../../assistant/wire";
import { ChatNetworkError } from "../../../../assistant/wire/transport";
import { decodeStep, stepPart } from "../../../../assistant/wire/trace";
import { FIXED_NOW, tokens, type Beat, type Scenario } from "./model";

/** An item and the time it is delivered, in milliseconds from the start of the run. */
export interface Timed<T> {
  readonly at: number;
  readonly item: T;
}

/** What the assistant's scripted transport replays: a frame, or an error thrown the way a real transport throws it. */
export type FrameItem = { readonly frame: Frame } | { readonly throw: Error };

/** The id the stream adapter gives a message that failed before `run` (the session injects a client id; the workbench pins it). */
export const CLIENT_ID = "client";

const offlineAt = (beats: readonly Beat[]): number | null => {
  const first = beats[0];
  return first !== undefined && first.kind === "offline" ? first.at : null;
};

/** The time of each token of a streamed piece: spread over its span, first at its start. */
const spread = (count: number, at: number, ms: number): number[] => Array.from({ length: count }, (_, i) => at + Math.round((ms * i) / Math.max(count, 1)));

/**
 * The chunk stream a mock adapter replays, built exactly the way `createStreamAdapter` builds it from
 * frames (part ids `<message>:t0`, `:r1`, `:w2` share one counter; a step is `<message>:<step id>`).
 * Two implementations of one mapping is the price of a fast chunk path; `parity.test.ts` pins them together.
 */
export function toChunks(scenario: Scenario, copy: { failed: string }): Timed<StreamChunk>[] {
  const out: Timed<StreamChunk>[] = [];
  const emit = (at: number, item: StreamChunk) => out.push({ at, item });
  const offline = offlineAt(scenario.beats);
  if (offline !== null) {
    emit(0, { type: "message-start", messageId: `local-${CLIENT_ID}`, createdAt: FIXED_NOW });
    emit(offline, { type: "error", message: copy.failed });
    return out;
  }
  const messageId = scenario.messageId;
  emit(0, { type: "message-start", messageId, createdAt: FIXED_NOW });

  let textPart: string | null = null;
  let thoughtPart: string | null = null;
  let parts = 0;
  const seen = new Set<string>();

  for (const beat of scenario.beats) {
    switch (beat.kind) {
      case "say": {
        thoughtPart = null;
        if (textPart === null) {
          textPart = `${messageId}:t${parts++}`;
          emit(beat.at, { type: "text-start", partId: textPart });
        }
        const pieces = tokens(beat.text);
        const times = spread(pieces.length, beat.at, beat.ms);
        pieces.forEach((delta, i) => emit(times[i] ?? beat.at, { type: "text-delta", partId: textPart as string, delta }));
        break;
      }
      case "think": {
        textPart = null;
        thoughtPart = `${messageId}:r${parts++}`;
        emit(beat.at, { type: "reasoning-start", partId: thoughtPart });
        const pieces = tokens(beat.text);
        const times = spread(pieces.length, beat.at, beat.ms);
        pieces.forEach((delta, i) => emit(times[i] ?? beat.at, { type: "reasoning-delta", partId: thoughtPart as string, delta }));
        emit(beat.at + beat.ms, { type: "reasoning-end", partId: thoughtPart, elapsedMs: beat.ms, ...(beat.tokens === undefined ? {} : { tokens: beat.tokens }) });
        thoughtPart = null;
        break;
      }
      case "step": {
        const decoded = decodeStep(beat.step, beat.eventSeq);
        if (decoded === null) break;
        if (!seen.has(decoded.stepId)) {
          seen.add(decoded.stepId);
          textPart = null;
        }
        emit(beat.at, { type: "step", part: stepPart(messageId, decoded) });
        break;
      }
      case "payload":
        textPart = null;
        emit(beat.at, { type: "data", part: { type: "data", id: `${messageId}:w${parts++}`, kind: beat.name, data: beat.data } });
        break;
      case "finish":
        emit(beat.at, { type: "finish" });
        break;
      case "fail":
        emit(beat.at, { type: "error", message: beat.message });
        break;
      case "lost":
        emit(beat.at, { type: "interrupted" });
        break;
      case "offline":
        break;
    }
  }
  return out;
}

/** The frame stream the assistant's scripted transport replays: the same run, spelled in the wire's own words. */
export function toFrames(scenario: Scenario): Timed<FrameItem>[] {
  const out: Timed<FrameItem>[] = [];
  const emit = (at: number, item: FrameItem) => out.push({ at, item });
  const frame = (at: number, raw: unknown) => {
    const decoded = decodeFrame(raw);
    if (decoded !== null) emit(at, { frame: decoded });
  };
  const offline = offlineAt(scenario.beats);
  if (offline !== null) {
    emit(offline, { throw: new ChatNetworkError() });
    return out;
  }
  frame(0, { type: "run", version: 1, thread_id: "capabilities", message_id: scenario.messageId, client_id: null, seq: null });
  frame(60, { type: "status", phase: "thinking" });

  for (const beat of scenario.beats) {
    switch (beat.kind) {
      case "say": {
        const pieces = tokens(beat.text);
        const times = spread(pieces.length, beat.at, beat.ms);
        pieces.forEach((delta, i) => frame(times[i] ?? beat.at, { type: "text_delta", delta }));
        break;
      }
      case "think": {
        const pieces = tokens(beat.text);
        const times = spread(pieces.length, beat.at, beat.ms);
        pieces.forEach((delta, i) => frame(times[i] ?? beat.at, { type: "reasoning_delta", delta }));
        frame(beat.at + beat.ms, { type: "reasoning_end", elapsed_ms: beat.ms, tokens: beat.tokens ?? null });
        break;
      }
      case "step":
        frame(beat.at, { type: "trace_step", event_seq: beat.eventSeq, step: beat.step });
        break;
      case "payload":
        frame(beat.at, { type: "ui_payload", kind: beat.name, data: beat.data });
        break;
      case "finish":
        frame(beat.at, { type: "done", finish_reason: "stop", tokens_in: null, tokens_out: null, cost_usd: null, replayed: false });
        break;
      case "fail":
        frame(beat.at, { type: "error", code: beat.code, message: beat.message });
        break;
      case "lost":
        emit(beat.at, { throw: new StreamLostError("network") });
        break;
      case "offline":
        break;
    }
  }
  return out;
}
