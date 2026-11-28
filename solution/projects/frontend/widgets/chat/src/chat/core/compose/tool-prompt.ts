/**
 * What the composer should say once a tool is picked.
 *
 * Picking states an intent, and for most tools the object arrives as the
 * sentence typed next — which is why the caret lands in the field and why this
 * returns nothing for them. A few tools want something a sentence cannot carry,
 * and today the interface stays silent: the turn sends, and the agent asks a
 * question the composer could have prevented.
 *
 * A HINT, never a gate. The turn still sends without the file; the agent still
 * asks. This only removes the round-trip when the user would have known.
 */

import type { Draft } from "./outbound";

/**
 * What a picked tool still wants. Mirrors the generated `ChatTool.needs`, which
 * is derived in Go from the tool's own required arguments.
 */
export type ToolNeed = "file" | "skill";

/**
 * The unmet need of the picks on this draft, or null when there is nothing to
 * say.
 *
 * Reads the DRAFT alone. The need travels on the pick, so this needs no
 * catalogue and no resolver — a second lookup here would be a second place that
 * can disagree with the row the user actually clicked.
 *
 * A `file` need is ALWAYS unmet: this surface is text-only, so nothing on the
 * draft can answer it. The hint is what tells the user to name the file in
 * words rather than reach for an affordance that is not there.
 *
 * The FIRST unmet need wins. Two picks wanting two different things is a
 * sentence, not a placeholder, and stacking them would produce a line nobody
 * can read — the second returns as soon as the first is met.
 */
export function unmetNeed(draft: Draft): ToolNeed | null {
  const picks = draft.pickedTools ?? [];
  if (picks.length === 0) return null;

  for (const pick of picks) {
    if (pick.needs === undefined) continue;
    return pick.needs;
  }
  return null;
}
