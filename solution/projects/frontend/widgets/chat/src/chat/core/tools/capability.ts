import type { ToolCatalogEntry } from "./menu/catalogue";

/**
 * The agent's arsenal — the composer's `+` menu.
 *
 * Absent ⇒ no `+` at all. A replay has no arsenal to offer.
 *
 * The catalogue is the HOST's: registration is conditional on the server's
 * capabilities, so a list shipped here would promise what a turn cannot deliver.
 *
 * A pick does NOT run the tool. Running one needs arguments and a form; the
 * agent decides how to do the work.
 */
export interface ToolsCapability {
  /** The catalogue, in the order it should be offered. */
  readonly entries: readonly ToolCatalogEntry[];
  /**
   * The server has not answered yet. `entries` is then EMPTY BECAUSE UNKNOWN,
   * not because it has none — three states, not two.
   *
   * Without it a slow answer renders identically to "no tools": the trigger
   * vanishes, reappears when the reply lands, and vanishes again on the next
   * room whose answer is not cached. The control holds its place instead.
   */
  readonly loading?: boolean;
  /**
   * Told that a pick happened, AFTER it is staged. Absent ⇒ nothing else runs.
   *
   * A notification, not a decision: the package stages the pick on the draft and
   * `buildOutbound` turns it into a marker, so a host that also composed text
   * here would make two writers of one outbound turn.
   */
  readonly onPick?: (entry: ToolCatalogEntry) => void;
}
