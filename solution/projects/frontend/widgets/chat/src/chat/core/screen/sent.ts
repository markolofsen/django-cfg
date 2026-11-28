/**
 * Did the reader just SEND, as opposed to receive?
 *
 * `use-stick-to-bottom` only follows growth while the view is already pinned, so
 * a reader scrolled into history stayed there when their own message landed —
 * the room looked as if nothing had been sent. Returning them is a different
 * question from "follow a streaming reply", and nothing answered it.
 *
 * The signal is the transcript itself rather than an event, because every entry
 * point ends there — Enter, the send button, a host calling `store.send`, a
 * queued prompt draining. `turn:sent` fires only on the keyboard path, so a
 * listener would have been right about a quarter of the ways to send.
 *
 * Pure, and here rather than in the hook, for the same reason as `MissedCount`:
 * the three cases it must tell apart are not visible in a rendered scroll
 * position, and getting any of them wrong is silent.
 */

/** Only the reader's own turn asks to be shown the bottom. */
export type SentRole = "user" | "assistant" | "system";

/**
 * @param previous the id list as last observed, or null before the first one
 * @param ids the id list now
 * @param roleOf the role the store holds for an id, or undefined if it has none
 */
export function isOwnSend(
  previous: readonly string[] | null,
  ids: readonly string[],
  roleOf: (id: string) => SentRole | undefined,
): boolean {
  // Nothing to compare against: the first observation is the room's existing
  // history, not something that just happened.
  if (previous === null) return false;

  // A send APPENDS exactly one id and leaves the rest identical.
  //
  // Compared as a WHOLE list, not by its tail, because the store outlives a room
  // switch: `load` replaces the transcript wholesale, and a room whose history
  // happens to end on a user message would otherwise read as a send and animate
  // a scroll every time it is opened. History paged in ABOVE fails this too,
  // which is correct — the reader asked for those rows where they are.
  if (ids.length !== previous.length + 1) return false;
  for (let index = 0; index < previous.length; index += 1) {
    if (ids[index] !== previous[index]) return false;
  }

  const last = ids[ids.length - 1];
  if (last === undefined) return false;
  // The assistant opening its reply also appends exactly one id. Following that
  // would drag a reader out of the history they scrolled up to read, which is
  // what the jump-to-latest control exists to offer instead of forcing.
  return roleOf(last) === "user";
}
