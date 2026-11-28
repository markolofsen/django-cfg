import type { MediaFailure } from "../domain";

/**
 * Translating what a media element reports into what the product says.
 *
 * Two different things arrive here and neither is the other:
 *
 *   - `MediaError` on the element, after an `error` event — a numeric code.
 *   - `DOMException` rejecting the `play()` promise — an autoplay refusal.
 *
 * Both end as a `MediaFailure`, which is a product vocabulary: the bar has to
 * NAME a cause, because unattributed silence is the failure this feature exists
 * to remove.
 */

/**
 * `MEDIA_ERR_ABORTED`. Fires whenever loading is interrupted — which includes
 * every ordinary `src` change and every navigation away.
 */
const MEDIA_ERR_ABORTED = 1;
const MEDIA_ERR_NETWORK = 2;
const MEDIA_ERR_DECODE = 3;
const MEDIA_ERR_SRC_NOT_SUPPORTED = 4;

/**
 * What an element's `error` event means, or `null` for "say nothing".
 *
 * **`null` is a real answer, not an absence of one.** Two cases produce it:
 *
 * 1. `error` fires with `media.error` already null — the spec permits it, and
 *    reading `.code` off it would throw inside an event listener.
 * 2. Code 1 is an ABORT, not a fault. The player changes `src` on every track
 *    switch, so surfacing it would show a failure on every ordinary switch —
 *    a phantom error attached to an action that worked.
 *
 * `machineId` is threaded in because a network failure on a remote file is not
 * a generic network failure: the machine went away, and naming it is the whole
 * point of the vocabulary.
 */
export function failureFromElement(
  error: MediaError | null,
  machineId?: string,
): MediaFailure | null {
  if (error === null) return null;
  switch (error.code) {
    case MEDIA_ERR_ABORTED:
      return null;
    case MEDIA_ERR_NETWORK:
      // The bytes stopped arriving. For a file on a machine that is the machine
      // becoming unreachable, which is a cause a person can act on.
      return { reason: "machine-unreachable", ...(machineId ? { machineId } : {}) };
    case MEDIA_ERR_DECODE:
    case MEDIA_ERR_SRC_NOT_SUPPORTED:
      // The relay served something this browser will not play. From the user's
      // side that is indistinguishable from a refusal to serve it.
      return { reason: "refused" };
    default:
      // Codes beyond the spec's 1-4 exist — 5 is encrypted media in at least one
      // implementation — so an unknown code still produces a named cause rather
      // than falling through to silence.
      return { reason: "unknown" };
  }
}

/**
 * What a rejected `play()` means.
 *
 * `NotAllowedError` is the autoplay policy: the browser wants a user gesture.
 * It is not a fault and the file is fine, so it maps to `blocked` — the one
 * member of the vocabulary that asks for a click rather than reporting a break.
 *
 * Anything else rejecting `play()` is a genuine failure to start.
 */
export function failureFromPlayRejection(cause: unknown): MediaFailure {
  const name = cause instanceof Error ? cause.name : "";
  return name === "NotAllowedError" ? { reason: "blocked" } : { reason: "unknown" };
}
