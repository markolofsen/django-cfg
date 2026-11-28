/**
 * The `sent` rungs of the recall ladder, read out of a room's transcript.
 *
 * `ladder.ts` WALKS the ladder; this builds the one array it walks. Split
 * because the walk is about keystrokes and this is about the room: they change
 * for unrelated reasons and neither needs the other to be tested.
 *
 * Derived from the transcript, never cached locally. The server is the SSoT for
 * "what did I send here", so the ladder matches what is on screen and works from
 * any browser or device — where a local copy is blind, and where it would also
 * outlive the room it belongs to.
 *
 * A localStorage cache did exist, to cover the moment before history arrives. It
 * went with the composer that consumed it: the surviving surface seeds from the
 * transcript it has already loaded, so the cache only ever had a wrong answer to
 * offer.
 */

/** Entries kept per room. Long enough to reach yesterday's prompt, short enough
 *  that the whole ladder stays walkable. */
const HISTORY_LIMIT = 50;

/** A single oversized paste must not evict the entire ladder. */
const MAX_ENTRY_LENGTH = 8_000;

/** The slice of a chat message the ladder cares about. */
interface LadderSource {
  role: string;
  content: string;
}

/**
 * The room's user-authored prompts, oldest first.
 *
 * Immediate repeats collapse so a double-send does not burn two ArrowUp steps.
 */
export function ladderFromMessages(messages: readonly LadderSource[]): string[] {
  const out: string[] = [];
  for (const m of messages) {
    if (m.role !== "user") continue;
    const text = m.content.trim();
    if (!text || text.length > MAX_ENTRY_LENGTH) continue;
    if (out[out.length - 1] === text) continue;
    out.push(text);
  }
  return out.slice(-HISTORY_LIMIT);
}
