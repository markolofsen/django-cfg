/**
 * Putting text into a composer that may already hold some.
 *
 * Three callers need this and each wrote its own: recall's Tab commit, a slash
 * pick, and taking a queued prompt back for editing. They disagreed on the one
 * question that matters — what happens to what the user already typed — so the
 * rule lives here once.
 */

/**
 * Would this write destroy something? `false` ⇒ write, and do NOT prompt.
 *
 * An empty field has nothing to lose, and re-inserting text the field already
 * holds is a no-op the user would read as a pointless question.
 */
export function needsChoice(current: string, incoming: string): boolean {
  const held = current.trim();
  if (held === "") return false;
  return held !== incoming.trim();
}
