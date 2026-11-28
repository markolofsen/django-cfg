import type { PartRenderer } from "../../primitives";
import { resolvePrivacy } from "../../core/run/privacy";
import { RunBlock } from "./block";
import type { RunOptions } from "./options";

/**
 * The renderer a host registers under `run`: `renderers={{ run: createRunRenderer(options) }}`.
 *
 * Opt-in. With it, adjacent thoughts, tool calls and trace steps of a turn are one
 * block (`planRuns`); without it the chat draws them one by one (the fold of settled
 * calls) as before. The privacy is resolved once here, so every block of the chat
 * shows the same, and a pattern that does not compile closes the detail rather than
 * opening it.
 */
export function createRunRenderer(options: RunOptions = {}): PartRenderer {
  const privacy = resolvePrivacy(options);
  return function RunRenderer({ part }) {
    return part.type === "run" ? <RunBlock run={part} options={options} privacy={privacy} /> : null;
  };
}
