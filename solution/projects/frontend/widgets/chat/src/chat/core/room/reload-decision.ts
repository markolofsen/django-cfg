/**
 * What to do when a room's revision moves.
 *
 * Split from the hook so the rule is testable without a renderer: every way
 * live-append can misbehave — reloading over a live stream, dropping a message
 * that arrived mid-turn, re-fetching the rows just read at mount — is decided
 * here.
 */
export type ReloadDecision = "reload" | "defer" | "ignore";

export interface ReloadInputs {
  /** The room's current revision. */
  readonly revision: number;
  /** The last revision this reader acted on (or mounted with). */
  readonly seen: number;
  /** True while a turn is streaming into the transcript. */
  readonly streaming: boolean;
  /** True when an earlier change was deferred and has not yet been served. */
  readonly deferred: boolean;
}

export function reloadDecision(input: ReloadInputs): ReloadDecision {
  const changed = input.revision !== input.seen;

  // Mid-stream, a change waits. Seeding replaces the transcript wholesale and
  // clears the streaming id, so reloading now would delete the reply as it is
  // being written.
  if (input.streaming) return changed || input.deferred ? "defer" : "ignore";

  // The stream ended with a change owed — serve it now. Without this branch a
  // message that landed mid-turn stays invisible until the room is reopened,
  // which is the original defect wearing a narrower window.
  if (input.deferred) return "reload";

  return changed ? "reload" : "ignore";
}
