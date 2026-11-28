/**
 * Message parts — the extension seam of this package.
 *
 * A new capability adds a PART TYPE here, never a prop to `<Chat>`. That is the
 * only shape whose API cost stays flat as the product grows: the predecessor
 * grew a prop per feature and reached 83, at which point no one could enumerate
 * the configurations it claimed to support (`@rules/architecture.md`).
 *
 * Shape follows the Vercel AI SDK's `message.parts` (a discriminated union keyed
 * on `type`, tool parts keyed by name) because the whole ecosystem converged on
 * it. We copy the SHAPE, not the package — its majors broke the API twice.
 */

import type { Attachment } from "../compose/attachments";
import type { MessageReply } from "../room/reply";

/**
 * Stable identity for a streamed part.
 *
 * Two consumers need it and neither can improvise one: the reducer routes
 * deltas by it, and React keys rows by it. An array index cannot serve — `reset`
 * empties the parts array mid-turn, so index 0 legitimately becomes a different
 * part and React reconciles the old DOM into it.
 */
export interface PartIdentity {
  readonly id: string;
}

/** Plain assistant or user prose. Markdown is a rendering concern, not a type. */
export interface TextPart extends PartIdentity {
  readonly type: "text";
  readonly text: string;
}

/**
 * How far one step of a turn got. The vocabulary of the trace (`assistant/wire/trace.ts`, the
 * server's `TraceStep.status`) and of the Run block; `pending` is the only one the
 * server never sends (a step the client knows is coming).
 *
 * `cancelled` is also what the reducer writes for a call still open when the turn
 * ended without its result: the reader sees "Stopped", never "Failed".
 */
export type StepStatus =
  | "pending"
  | "running"
  | "ok"
  | "error"
  | "skipped"
  | "cancelled"
  | "timeout"
  | "denied";

/**
 * What the server removed from a step's detail before sending it.
 * An unknown value is read as `omitted` (fail closed), so a reader never shows
 * more than a newer server meant to.
 */
export type StepRedaction = "none" | "masked" | "omitted";

/** A source a step touched: a document, a page, a record. A title, never a link. */
export interface StepRef {
  readonly kind: string;
  readonly id: string;
  readonly title?: string;
}

/**
 * What a step carries beyond its part's own fields, all optional and additive:
 * a part from a producer that knows nothing of traces has none of it.
 *
 * Durations and offsets are the SERVER's milliseconds; the client clock is used
 * only for the live counter. `argsView` and `resultView` are the views the server
 * decided may leave it (`redaction` says how), never the raw `input` / `output`.
 */
export interface StepMeta {
  readonly status?: StepStatus;
  /** What the step is for: `retriever`, `read`, `write`, `propose`. Open set. */
  readonly role?: string;
  /** A readable title and a readable outcome, both written by the server. */
  readonly label?: string;
  readonly summary?: string;
  /** Why the step ran, and what it searched for. Level 2 and above only. */
  readonly purpose?: string;
  readonly query?: string;
  readonly argsView?: Readonly<Record<string, unknown>>;
  readonly argsBytes?: number;
  readonly resultView?: string;
  readonly resultBytes?: number;
  readonly truncated?: boolean;
  readonly redaction?: StepRedaction;
  /** Milliseconds since the trace began, and how long the step took. */
  readonly startedMs?: number;
  readonly durationMs?: number;
  readonly errorCode?: string;
  readonly retryable?: boolean;
  /** The step this one ran under (a tool under its model request). */
  readonly parentId?: string;
  /** Steps that ran in parallel share a group. */
  readonly group?: string;
  readonly attempt?: number;
  readonly retryOf?: string;
  readonly sources?: readonly StepRef[];
  /** The frame's order; a replayed or late older frame never overwrites a newer one. */
  readonly eventSeq?: number;
  /** A thought whose words never left the server: only its size is known. */
  readonly hidden?: boolean;
  /** The model that answered a model step, and what the step cost. */
  readonly model?: string;
  readonly tokens?: StepTokens;
  readonly costUsd?: number;
}

/** Tokens a step spent, each only when the engine reported it. */
export interface StepTokens {
  readonly input?: number;
  readonly output?: number;
  readonly reasoning?: number;
  readonly cached?: number;
}

/**
 * Model thinking. Separate from `text` because it collapses by default and is
 * never part of the copyable answer.
 */
export interface ReasoningPart extends PartIdentity {
  readonly type: "reasoning";
  readonly text: string;
  /**
   * Still thinking. The block shows a live label while true and a settled
   * summary once false.
   *
   * Needed because a thought is sealed by the NEXT part opening, not by a
   * chunk of its own — without this the transcript cannot tell a thought still
   * arriving from one that finished, and both would render identically.
   */
  readonly streaming?: boolean;
  /**
   * Measured wall time, when the engine measured it. Absent is ordinary — a
   * driven CLI engine reports no duration — so the block must read without it.
   */
  readonly elapsedMs?: number;
  /**
   * Reasoning tokens spent, when the engine reports them.
   *
   * The only true thing left to show when a provider ships the thinking block
   * with its words stripped: `text` is "" and this is not. A block keyed on
   * text alone renders nothing on the engine most likely to be running.
   */
  readonly tokens?: number;
  /** Trace detail, when a trace step produced this part. */
  readonly meta?: StepMeta;
}

/**
 * Tool-call lifecycle. Four states, and the transition carries the payload —
 * so a renderer can never read `output` before it exists.
 *
 * Modelled as a union rather than a `status` field plus optional `input`/
 * `output`: the predecessor's `ToolCall` had `status` alongside optional
 * `output`, which let "success with no output" and "still running" become the
 * same value at the type level.
 */
export type ToolState =
  /** Arguments are still streaming in; `input` is a partial JSON string. */
  | { readonly state: "input-streaming"; readonly inputText: string }
  /** Arguments complete, execution not finished. */
  | { readonly state: "input-available"; readonly input: unknown }
  | { readonly state: "output-available"; readonly input: unknown; readonly output: unknown }
  | { readonly state: "output-error"; readonly input: unknown; readonly error: string };

/**
 * One tool invocation.
 *
 * `messages` is present from day one deliberately, ahead of any renderer for it:
 * a tool that spawns a subagent carries that subagent's whole conversation, and
 * assistant-ui showed this is the shape that works (nested read-only thread,
 * parent tool renderers inherited inward). Retrofitting a nested thread onto a
 * flat transcript later is a rewrite of every selector; reserving the field now
 * costs one line.
 */
export interface ToolPart extends PartIdentity {
  readonly type: "tool";
  /** `id` IS the tool-call id — the wire's `toolCallId` maps onto it directly.
   *  A second field holding the same value is a second source of truth. */
  readonly toolName: string;
  readonly toolState: ToolState;
  /** Subagent transcript, when this tool ran one. Absent for an ordinary tool. */
  readonly messages?: readonly ChatMessage[];
  /** Trace detail, when a trace step produced this part; the settled outcome of an unfinished call also lives here. */
  readonly meta?: StepMeta;
}

/**
 * Product-specific typed content the agent authored (map, chart, image card…).
 * `data` stays `unknown`: the renderer registry validates per kind, so an
 * unknown or malformed kind degrades to a fallback instead of widening this
 * union every time the agent learns a new block.
 */
export interface DataPart extends PartIdentity {
  readonly type: "data";
  readonly kind: string;
  readonly data: unknown;
}

/**
 * A file the sender attached. Rendered by the host's `attachment` renderer
 * (the assistant ships one); absent renderer draws nothing, like any part.
 */
export interface AttachmentPart extends PartIdentity {
  readonly type: "attachment";
  readonly attachment: Attachment;
}

/** The `data` kinds the package draws itself (interactive blocks). A host's renderer list never has to name them. */
export const BLOCK_KINDS = ["ask", "approval", "changes"] as const;

export type MessagePart = TextPart | ReasoningPart | ToolPart | DataPart | AttachmentPart;

/**
 * Adjacent trace parts (thoughts, tool calls, trace steps) drawn as ONE block.
 *
 * Render-only: it is built from a message's parts at draw time, never streamed,
 * stored or reduced, which is why it is not in {@link MessagePart}. A host opts in
 * by registering a renderer under the `run` type.
 */
export interface RunPart extends PartIdentity {
  readonly type: "run";
  readonly parts: readonly MessagePart[];
}

export type MessageRole = "user" | "assistant" | "system";

/**
 * Terminal state of an assistant turn.
 *
 * `interrupted` and `failed` are distinct because the RECOVERY differs: an
 * interrupted turn may still have been persisted by the server and reconciles on
 * reconnect, while a failed one is a verdict the server already recorded. The
 * predecessor learned this the expensive way — a failure rendered as an ordinary
 * reply looks like the agent said it, which is worse than silence.
 */
export type MessageStatus =
  | { readonly state: "streaming" }
  | { readonly state: "complete" }
  | { readonly state: "interrupted" }
  | { readonly state: "failed"; readonly message: string };

/** Whose turn a `user` message is: this seat's own, or another participant's. */
export type MessageFrom = "me" | "other";

export interface ChatMessage {
  readonly id: string;
  readonly role: MessageRole;
  readonly parts: readonly MessagePart[];
  readonly status: MessageStatus;
  /** Wall-clock creation, millis. Ordering uses array position, never this. */
  readonly createdAt: number;
  /**
   * WHO spoke this turn, as the host's own opaque reference — never a name.
   *
   * The package neither resolves nor renders it: a host with several speakers
   * in one room passes a header slot that turns this into a line, and a host
   * with one correspondent passes nothing. Absent on every turn the host does
   * not attribute, which is the ordinary case.
   */
  readonly authorId?: string;
  /**
   * The message this one answers, as the host's own id.
   *
   * Rendered only where the host supplies a quote resolver — the package holds
   * no transcript index and will not search one. Absent is the ordinary case.
   */
  readonly replyTo?: string;
  /**
   * Whether a `user` turn was written by ANOTHER participant of the room.
   *
   * Absent means this seat's own turn, which is every turn a one-to-one chat
   * has. The host sets `"other"` on what it receives for someone else; it is
   * what draws the turn as a left-hand bubble instead of the sender's own.
   */
  readonly from?: MessageFrom;
  /**
   * The turn is a private line: only its author and `with` (the other party's name) read it.
   * Absent on a line for the whole room, which is the ordinary case.
   */
  readonly private?: { readonly with: string };
  /** How the host wants the row marked: it names this seat (`mention`) or is a private line (`private`). Absent: not marked. */
  readonly highlight?: "mention" | "private";
  /** How far the assistant is with this line, when it took it. Absent: it did not, or has not said. */
  readonly reply?: MessageReply;
}

/** A turn another participant wrote: drawn on the reader's left, in its own bubble. */
export const isOtherParticipant = (m: ChatMessage): boolean =>
  m.role === "user" && m.from === "other";

/** Narrowing helpers — cheaper than repeating the discriminant at every call site. */
export const isTextPart = (p: MessagePart): p is TextPart => p.type === "text";
export const isToolPart = (p: MessagePart): p is ToolPart => p.type === "tool";

/** A tool part that ran a subagent, i.e. one a nested thread can render. */
export function subagentMessages(part: ToolPart): readonly ChatMessage[] | undefined {
  return part.messages !== undefined && part.messages.length > 0 ? part.messages : undefined;
}

/** True once the tool produced something a renderer can show. */
export function toolHasResult(part: ToolPart): boolean {
  const s = part.toolState.state;
  return s === "output-available" || s === "output-error";
}
