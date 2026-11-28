/**
 * The transcript reducer — the ONE place a stream becomes messages.
 *
 * Pure and synchronous on purpose: every streaming bug the predecessor shipped
 * (duplicated fragments after a retry, tool output attached to the wrong call,
 * a failed turn rendered as a normal reply) is reproducible here in
 * milliseconds, with no React and no DOM. `@rules/testing.md` calls this the
 * main rung for exactly that reason.
 *
 * Normalized as `ids[] + byId{}` so a message can re-render without the list
 * re-rendering — the transcript subscribes to ids, each row to its own id.
 */

import type { StreamChunk } from "./chunks";
import type { ChatMessage, MessagePart, MessageStatus, ToolState } from "./parts";
import { isOpenStatus, stepMetaOf } from "../run/trace";
import { settleOpenParts } from "./settle";

/** A tool chunk that names a call by id and is not the one that opens it. */
type ToolFollowUp = Extract<
  StreamChunk,
  { type: "tool-input-delta" | "tool-input-available" | "tool-output" | "tool-error" }
>;

/** How many calls, and how many chunks of each, wait for a start that has not arrived. */
const MAX_ORPHAN_CALLS = 16;
const MAX_ORPHAN_CHUNKS = 16;

export interface TranscriptState {
  readonly ids: readonly string[];
  readonly byId: Readonly<Record<string, ChatMessage>>;
  /** The message currently receiving chunks, if any. */
  readonly streamingId: string | null;
  /**
   * Tool chunks that arrived before their `tool-input-start`, by call id, applied
   * when it comes. Bounded, and gone when the turn ends or restarts: a result whose
   * call never opens is not a part, and keeping it forever would be a leak.
   */
  readonly orphans?: Readonly<Record<string, readonly ToolFollowUp[]>>;
}

export const emptyTranscript: TranscriptState = { ids: [], byId: {}, streamingId: null };

function replacePart(
  message: ChatMessage,
  at: number,
  part: MessagePart,
): ChatMessage {
  const parts = message.parts.slice();
  parts[at] = part;
  return { ...message, parts };
}

function appendPart(message: ChatMessage, part: MessagePart): ChatMessage {
  return { ...message, parts: [...message.parts, part] };
}

/**
 * Append the part, or REPLACE the one already carrying that id.
 *
 * For WHOLE parts only — `file` and `data`, which arrive complete in one chunk.
 * A repeated id there is the same part revised, never a second part: the
 * server re-sends its plan block under the stable id `plan-current` on every
 * step, and the transport's own accumulator (`collectBlock`,
 * `transport/web/chat-map.ts`) is replace-by-id for exactly that reason. A
 * blind append stacks one plan card per step.
 *
 * Deliberately NOT used by `text-start` / `reasoning-start` / `tool-input-start`,
 * which create an EMPTY part that deltas then fill. Replacement there would let
 * a repeated start chunk wipe the text already accumulated under that id —
 * strictly worse than the duplicate empty part it would be preventing.
 *
 * Replacement keeps the ORIGINAL position rather than moving the part to the
 * end: the plan was authored where it first appeared, and a card that jumps
 * down the transcript on each revision makes a different claim about the turn.
 */
function upsertPart(message: ChatMessage, part: MessagePart): ChatMessage {
  const at = message.parts.findIndex((p) => p.id === part.id);
  if (at === -1) return appendPart(message, part);
  const parts = [...message.parts];
  parts[at] = part;
  return { ...message, parts };
}

function withMessage(state: TranscriptState, message: ChatMessage): TranscriptState {
  const known = message.id in state.byId;
  return {
    ...state,
    ids: known ? state.ids : [...state.ids, message.id],
    byId: { ...state.byId, [message.id]: message },
  };
}

const withoutOrphans = ({ orphans: _orphans, ...rest }: TranscriptState): TranscriptState => rest;

/** Locate a part by key, or -1. Keys are unique within a message by construction. */
function findPart(
  message: ChatMessage,
  match: (part: MessagePart) => boolean,
): number {
  for (let i = message.parts.length - 1; i >= 0; i -= 1) {
    const part = message.parts[i];
    if (part !== undefined && match(part)) return i;
  }
  return -1;
}

function findTool(message: ChatMessage, toolCallId: string): number {
  return findPart(message, (p): boolean => p.type === "tool" && p.id === toolCallId);
}

/** Preserve the input we already have when a state transition does not carry it. */
function inputOf(state: ToolState): unknown {
  return state.state === "input-streaming" ? undefined : state.input;
}

/**
 * Text and reasoning deltas share everything but the discriminant, so they
 * share the code — a copied pair drifts, and the two paths must stay identical
 * or `reset` will clear one and not the other.
 */
function applyDelta(
  message: ChatMessage,
  kind: "text" | "reasoning",
  partId: string,
  delta: string,
): ChatMessage {
  const at = findPart(message, (p) => p.type === kind && p.id === partId);
  if (at < 0) return message;
  const part = message.parts[at];
  if (part === undefined || (part.type !== "text" && part.type !== "reasoning")) return message;
  return replacePart(message, at, { ...part, text: part.text + delta });
}

export function reduce(state: TranscriptState, chunk: StreamChunk): TranscriptState {
  switch (chunk.type) {
    case "message-start": {
      const message: ChatMessage = {
        id: chunk.messageId,
        role: "assistant",
        parts: [],
        status: { state: "streaming" },
        createdAt: chunk.createdAt,
      };
      return { ...withMessage(withoutOrphans(state), message), streamingId: chunk.messageId };
    }
    case "reset": {
      const current = currentMessage(state);
      if (current === null) return state;
      return withMessage(withoutOrphans(state), { ...current, parts: [] });
    }
    case "finish":
      return finishWith(state, { state: "complete" });
    case "error":
      return finishWith(state, { state: "failed", message: chunk.message });
    case "interrupted":
      return finishWith(state, { state: "interrupted" });
    default:
      return reduceIntoCurrent(state, chunk);
  }
}

function currentMessage(state: TranscriptState): ChatMessage | null {
  if (state.streamingId === null) return null;
  return state.byId[state.streamingId] ?? null;
}

function finishWith(state: TranscriptState, status: MessageStatus): TranscriptState {
  const current = currentMessage(state);
  if (current === null) return state;
  return {
    ...withMessage(withoutOrphans(state), { ...settleOpenParts(current), status }),
    streamingId: null,
  };
}

/**
 * Chunks that target the in-flight message.
 *
 * A chunk arriving with no message in flight is DROPPED rather than implicitly
 * opening one. Silent auto-creation hides an adapter that forgot
 * `message-start`, and the resulting transcript looks plausible while being
 * wrong — the failure has to be visible in a test, not smoothed over.
 */
function reduceIntoCurrent(
  state: TranscriptState,
  chunk: Exclude<StreamChunk, { type: "message-start" | "reset" | "finish" | "error" | "interrupted" }>,
): TranscriptState {
  const current = currentMessage(state);
  if (current === null) return state;

  switch (chunk.type) {
    case "text-start":
      // A repeated start keeps what the part already holds: the same id is the same part.
      if (findPart(current, (p) => p.type === "text" && p.id === chunk.partId) >= 0) return state;
      return withMessage(
        state,
        appendPart(current, { type: "text", id: chunk.partId, text: "" }),
      );
    case "text-delta":
      return withMessage(state, applyDelta(current, "text", chunk.partId, chunk.delta));
    case "reasoning-start":
      if (findPart(current, (p) => p.type === "reasoning" && p.id === chunk.partId) >= 0) return state;
      return withMessage(
        state,
        appendPart(current, {
          type: "reasoning",
          id: chunk.partId,
          text: "",
          streaming: true,
        }),
      );
    case "reasoning-delta":
      return withMessage(state, applyDelta(current, "reasoning", chunk.partId, chunk.delta));
    case "reasoning-end": {
      const at = findPart(current, (p) => p.type === "reasoning" && p.id === chunk.partId);
      const part = at < 0 ? undefined : current.parts[at];
      // An end for a block that never opened is dropped rather than synthesised:
      // a part with no text and no measurement is an empty disclosure.
      if (part === undefined || part.type !== "reasoning") return state;
      return withMessage(
        state,
        replacePart(current, at, {
          ...part,
          streaming: false,
          // Keep what the engine measured; absent stays absent rather than
          // becoming a zero, which would read as "thought for 0ms".
          ...(chunk.elapsedMs === undefined ? {} : { elapsedMs: chunk.elapsedMs }),
          ...(chunk.tokens === undefined ? {} : { tokens: chunk.tokens }),
        }),
      );
    }
    case "tool-input-start": {
      // Idempotent by call id: a repeated start (a replayed frame) neither appends a
      // second card nor wipes the arguments already received.
      if (findTool(current, chunk.toolCallId) >= 0) return state;
      const opened = withMessage(
        state,
        appendPart(current, {
          type: "tool",
          id: chunk.toolCallId,
          toolName: chunk.toolName,
          toolState: { state: "input-streaming", inputText: "" },
        }),
      );
      return applyOrphans(opened, chunk.toolCallId);
    }
    case "tool-input-delta":
    case "tool-input-available":
    case "tool-output":
    case "tool-error":
      return reduceToolFollowUp(state, current, chunk);
    case "data":
      return withMessage(state, upsertPart(current, chunk.part));
    case "step":
      return reduceStep(state, current, chunk.part);
  }
}

/**
 * A chunk for a call that is already open, or one waiting for its start.
 *
 * The first answer a call gets is final: a repeated output, error or
 * availability after it settled changes nothing, so a replayed frame cannot turn a
 * failure back into a success or the reverse.
 */
function reduceToolFollowUp(
  state: TranscriptState,
  current: ChatMessage,
  chunk: ToolFollowUp,
): TranscriptState {
  const at = findTool(current, chunk.toolCallId);
  if (at < 0) return keepOrphan(state, chunk);
  const part = current.parts[at];
  if (part === undefined || part.type !== "tool") return state;
  const settled = part.toolState.state === "output-available" || part.toolState.state === "output-error";

  switch (chunk.type) {
    case "tool-input-delta":
      return part.toolState.state === "input-streaming"
        ? withMessage(state, replacePart(current, at, { ...part, toolState: { state: "input-streaming", inputText: part.toolState.inputText + chunk.delta } }))
        : state;
    case "tool-input-available":
      return settled ? state : withMessage(state, replacePart(current, at, { ...part, toolState: { state: "input-available", input: chunk.input } }));
    case "tool-output":
      return settled ? state : withMessage(state, replacePart(current, at, { ...part, toolState: { state: "output-available", input: inputOf(part.toolState), output: chunk.output } }));
    case "tool-error":
      return settled ? state : withMessage(state, replacePart(current, at, { ...part, toolState: { state: "output-error", input: inputOf(part.toolState), error: chunk.error } }));
  }
}

function keepOrphan(state: TranscriptState, chunk: ToolFollowUp): TranscriptState {
  const waiting = state.orphans ?? {};
  const queue = waiting[chunk.toolCallId];
  if (queue === undefined && Object.keys(waiting).length >= MAX_ORPHAN_CALLS) return state;
  if (queue !== undefined && queue.length >= MAX_ORPHAN_CHUNKS) return state;
  return { ...state, orphans: { ...waiting, [chunk.toolCallId]: [...(queue ?? []), chunk] } };
}

/** Apply what arrived ahead of this call's start, in arrival order. */
function applyOrphans(state: TranscriptState, toolCallId: string): TranscriptState {
  const queue = state.orphans?.[toolCallId];
  if (queue === undefined) return state;
  const { [toolCallId]: _applied, ...rest } = state.orphans ?? {};
  let next: TranscriptState = { ...state, orphans: rest };
  for (const chunk of queue) {
    const current = currentMessage(next);
    if (current === null) break;
    next = reduceToolFollowUp(next, current, chunk);
  }
  return next;
}

/**
 * A trace step: appended the first time, then replaced IN PLACE by its later frames.
 *
 * An older frame never overwrites a newer one: a replayed or reordered `running`
 * after the step settled would put a finished call back to spinning. The frame's
 * own order (`eventSeq`) decides; where a producer sent none, a settled step is
 * simply never reopened.
 */
function reduceStep(
  state: TranscriptState,
  current: ChatMessage,
  part: Extract<StreamChunk, { type: "step" }>["part"],
): TranscriptState {
  const at = findPart(current, (p) => p.id === part.id);
  if (at < 0) return withMessage(state, appendPart(current, part));
  const held = current.parts[at];
  const before = held === undefined ? undefined : stepMetaOf(held);
  const after = stepMetaOf(part);
  if (before?.eventSeq !== undefined && after?.eventSeq !== undefined && after.eventSeq <= before.eventSeq) return state;
  if (before !== undefined && !isOpenStatus(before.status) && isOpenStatus(after?.status)) return state;
  return withMessage(state, replacePart(current, at, part));
}

/** Append a message the user authored. Never streams, so it lands complete. */
export function appendUserMessage(
  state: TranscriptState,
  message: ChatMessage,
): TranscriptState {
  return withMessage(state, message);
}

/**
 * Add a message the host received from elsewhere, or replace the copy it holds.
 *
 * It is not a turn: nothing is sent, no stream opens, and `streamingId` is left
 * exactly as it was, so a remote message landing mid-answer cannot cut the live
 * one short. The one thing refused is a copy of the streaming message itself.
 * The stream owns that id until it finishes, and a polled snapshot of the
 * half-written reply would overwrite parts the reducer is still extending.
 *
 * A known id is replaced in place and keeps its position, so a host that
 * re-delivers a message (an optimistic row confirmed by the server, a poll that
 * overlaps the last one) changes nothing about the order.
 */
export function receiveMessage(
  state: TranscriptState,
  message: ChatMessage,
): TranscriptState {
  if (message.id === state.streamingId) return state;
  if (state.byId[message.id] === message) return state;
  return withMessage(state, message);
}

export function reduceAll(
  state: TranscriptState,
  chunks: readonly StreamChunk[],
): TranscriptState {
  return chunks.reduce(reduce, state);
}

export function selectMessages(state: TranscriptState): readonly ChatMessage[] {
  return state.ids.flatMap((id) => {
    const message = state.byId[id];
    return message === undefined ? [] : [message];
  });
}
