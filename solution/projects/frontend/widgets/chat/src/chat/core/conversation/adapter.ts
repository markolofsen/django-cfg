/**
 * The backend contract. ONE required method.
 *
 * Everything optional an adapter might do — mentions, retry — is a
 * separate capability object, not a field here. That split is what keeps the
 * root component at seven props: a capability that is absent is a feature that
 * is off, expressed once, instead of a boolean plus its four companion props.
 *
 * A `ReadableStream` rather than a callback bag because backpressure and
 * cancellation come with it: `AbortSignal` stops the stream and the reducer
 * needs no "am I still the current turn?" bookkeeping.
 */

import type { Attachment } from "../compose/attachments";
import type { Recipient } from "../room/recipient";
import type { StreamChunk } from "./chunks";
import type { ChatMessage } from "./parts";

export interface SendRequest {
  /** The full outbound text, tool markers already appended. */
  readonly text: string;
  /** Prior turns, oldest first. The adapter decides how much it forwards. */
  readonly history: readonly ChatMessage[];
  /** The message this turn answers, or absent. Opaque — the adapter forwards it. */
  readonly replyTo?: string;
  /** Who the turn is for. `all` for a draft that chose no one. */
  readonly recipient: Recipient;
  /** The seats the text names with `@`, for highlights and badges (never for who may read it). */
  readonly mentions: readonly string[];
  /**
   * The id of the optimistic message this turn put in the transcript.
   *
   * A host whose server dedupes on a sender-made id (the room's `client_id`) sends this, and reuses it on a retry,
   * so one line can never be posted twice.
   */
  readonly messageId: string;
  /** Files attached to this turn, already stored. Empty when none. How the model sees them is the adapter's call. */
  readonly attachments: readonly Attachment[];
  /** The model id chosen in the composer (`capabilities.models`), when the host offers a choice. */
  readonly model?: string;
  readonly signal: AbortSignal;
}

export interface ChatAdapter {
  sendMessage(request: SendRequest): Promise<ReadableStream<StreamChunk>>;
}
