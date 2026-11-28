/**
 * How many replies arrived while the reader was scrolled away.
 *
 * A plain class for the same reason as `BottomPin`: nothing here is DOM. What
 * is hard is deciding when the count starts, when it resets, and what counts —
 * and all three are wrong in ways a rendered badge cannot show you.
 *
 * No store: the transcript already knows the message list and the pin state, so
 * a second owner for "how far behind is the reader" could disagree with the
 * scroll position it is describing.
 */

/**
 * The reader's own messages never count.
 *
 * Sending scrolls them to the bottom anyway, so a `user` row can only enter the
 * count in a race — and a badge that says "1 new" pointing at your own sentence
 * is worse than no badge. Mirrors the server's unread rule, which excludes
 * `author_kind = 'human'` for exactly this reason.
 */
export type MissedRole = "user" | "assistant" | "system";

export class MissedCount {
  /**
   * The last row present when the reader left the bottom. Null while pinned.
   *
   * An id, not a length and not a set of every id seen. A length breaks when
   * history loads ABOVE — the list grows without anything arriving. A set
   * breaks the same way for the opposite reason: prepended rows are absent from
   * it and read as new. New messages append, so the last row is the frontier,
   * and everything after it is what the reader missed.
   */
  private frontier: string | null = null;
  /** Distinguishes "pinned, no frontier" from "unpinned on an empty list". */
  private armed = false;
  private count = 0;

  /**
   * Feed the current state after every render.
   *
   * @param pinned whether the viewport is following the bottom
   * @param rows every message currently in the transcript, in order
   */
  observe(pinned: boolean, rows: readonly { id: string; role: MissedRole }[]): void {
    if (pinned) {
      this.frontier = null;
      this.armed = false;
      this.count = 0;
      return;
    }
    // The FIRST unpinned observation sets the frontier. An empty transcript
    // leaves it null, which correctly means every later row is new.
    if (!this.armed) {
      this.frontier = rows.at(-1)?.id ?? null;
      this.armed = true;
    }
    const at = this.frontier === null ? -1 : rows.findIndex((row) => row.id === this.frontier);
    // A frontier that vanished (a cleared transcript, a room switch) must not
    // count the whole list: -1 there would make every row new. Re-arm instead.
    if (this.frontier !== null && at === -1) {
      this.frontier = rows.at(-1)?.id ?? null;
      this.count = 0;
      return;
    }
    this.count = rows.slice(at + 1).filter((row) => row.role !== "user").length;
  }

  /**
   * The badge's number, or null when there is nothing honest to show.
   *
   * Null rather than 0 so a caller cannot render an empty badge: "the button is
   * showing but nothing arrived" and "1 arrived" are different states, and only
   * the second deserves a number.
   */
  value(): number | null {
    return this.count > 0 ? this.count : null;
  }
}

/**
 * The transcript's id list paired with the roles the store holds for it.
 *
 * Separate from the React binding so the one decision it makes is testable
 * without a DOM: what to do with an id the store has no message for. It DROPS
 * that row. The alternative — defaulting a role — has to pick one, and every
 * choice is wrong in a way the badge shows: `assistant` counts a phantom and
 * sends the reader down to a row that is not there, `user` silently suppresses
 * a real reply if the guess is ever wrong.
 *
 * `ids` and the message map are written together in every store path, so the
 * case cannot arise today. It is written down because the two consumers of that
 * invariant had drifted apart: `selectMessages` already drops the missing id,
 * while this side used to substitute `assistant`.
 *
 * Structural parameter rather than the store's own types: `core` may import
 * only `utils`.
 */
export function missedRows(
  ids: readonly string[],
  byId: Readonly<Record<string, { readonly role: MissedRole } | undefined>>,
): readonly { id: string; role: MissedRole }[] {
  return ids.flatMap((id) => {
    const message = byId[id];
    return message === undefined ? [] : [{ id, role: message.role }];
  });
}
