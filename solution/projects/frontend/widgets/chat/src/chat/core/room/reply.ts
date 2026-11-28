/**
 * How far the assistant is with one line it took, as the host learns it (the room's poll).
 *
 * `working`: it is writing. `answered`: its reply is in the chat. `failed`: it could not (`code` says why); the author may retry.
 * A line the assistant did not take has no reply at all, and shows nothing.
 */
export type ReplyState = "working" | "answered" | "failed";

export interface MessageReply {
  readonly state: ReplyState;
  /** With `failed`: the server's reason, for the host to word. */
  readonly code?: string;
}
