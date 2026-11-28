/**
 * The wire vocabulary between an adapter and this package.
 *
 * An adapter's ONLY obligation is to emit these. It does not build messages,
 * hold state, or know about React — so a new backend is one file, and the
 * reducer stays the single owner of how a transcript is assembled.
 *
 * Chunks name PART ids explicitly (`partId`) rather than implying "the last
 * part". Implicit targeting is what makes interleaved output — text, then a
 * tool, then more text — collapse into the wrong part; naming it costs the
 * adapter nothing since it already knows which stream it is reading.
 */

import type { DataPart, ReasoningPart, ToolPart } from "./parts";

export type StreamChunk =
  /**
   * A new assistant message begins. Everything after targets this message.
   *
   * `createdAt` comes from the adapter because the core reads no clock: a
   * reducer that called `Date.now()` would make every transcript test
   * time-dependent, and history replay would stamp old turns with now.
   */
  | { readonly type: "message-start"; readonly messageId: string; readonly createdAt: number }
  | { readonly type: "text-start"; readonly partId: string }
  | { readonly type: "text-delta"; readonly partId: string; readonly delta: string }
  | { readonly type: "reasoning-start"; readonly partId: string }
  | { readonly type: "reasoning-delta"; readonly partId: string; readonly delta: string }
  /**
   * The thought is finished — the only chunk that can say so.
   *
   * Without it a block is sealed by the NEXT part opening, which leaves the
   * last thought of a turn streaming forever when the model answers with a
   * tool call, or with nothing at all. `elapsedMs` and `tokens` carry whatever
   * the engine measured; both absent is ordinary.
   */
  | {
      readonly type: "reasoning-end";
      readonly partId: string;
      readonly elapsedMs?: number;
      readonly tokens?: number;
    }
  /** Arguments begin streaming; the part appears immediately, in `input-streaming`. */
  | { readonly type: "tool-input-start"; readonly toolCallId: string; readonly toolName: string }
  | { readonly type: "tool-input-delta"; readonly toolCallId: string; readonly delta: string }
  | { readonly type: "tool-input-available"; readonly toolCallId: string; readonly input: unknown }
  | { readonly type: "tool-output"; readonly toolCallId: string; readonly output: unknown }
  | { readonly type: "tool-error"; readonly toolCallId: string; readonly error: string }
  | { readonly type: "data"; readonly part: DataPart }
  /**
   * One trace step as a whole part, sent when it starts and again when it settles
   * under the SAME part id. The reducer replaces it in place (never appends a second
   * row) and refuses a frame older than the one it holds.
   */
  | { readonly type: "step"; readonly part: ToolPart | ReasoningPart | DataPart }
  /**
   * Discard everything accumulated for the current message and start it over —
   * the agent is re-issuing the turn after a mid-stream cut.
   *
   * An INSTRUCTION, not a notice. Ignoring it renders the abandoned fragment
   * followed by the real one, which reads as the agent repeating itself.
   */
  | { readonly type: "reset" }
  | { readonly type: "finish" }
  /** The server reported the turn as failed. Terminal, and durable server-side. */
  | { readonly type: "error"; readonly message: string }
  /**
   * The transport died without a terminal frame. NOT a failure verdict: the
   * reply may or may not have been persisted, so the host reconciles on
   * reconnect rather than showing a permanent error.
   */
  | { readonly type: "interrupted" };
