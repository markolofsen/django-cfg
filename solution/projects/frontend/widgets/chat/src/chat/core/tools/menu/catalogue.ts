// The tool catalogue as data. Registration on the server is conditional on
// what it can reach, so the list is read, never assumed.
//
// May import: ./rank.

import { scoreTool } from "./rank";

/** One capability, as the registry already describes it. */
export interface ToolCatalogEntry {
  /** The registry's own name, e.g. `transcribe_audio`. Also what a pick names. */
  readonly id: string;
  /** What the row READS. Short enough for a narrow pane. */
  readonly name: string;
  /**
   * One human line, authored separately from the tool's own description — that
   * one is model-facing and mostly disambiguation against neighbouring tools.
   */
  readonly summary: string;
  /** The registry's grouping key (`stt`, `web`, `disk`, …), used verbatim. */
  readonly category: string;
  /**
   * The registry's own search keywords. Searching "voice" must reach a tool
   * spelled `transcribe_audio`.
   */
  readonly keywords?: readonly string[];
  /**
   * Glyph KEY, never a node — the catalogue crosses the transport as data. An unmapped
   * key draws nothing rather than failing.
   */
  readonly icon?: string;
  /**
   * What a pick still wants, when anything.
   *
   * Absent for most tools by design: picking states an intent and the object
   * arrives as the sentence typed next. The exceptions want something a
   * sentence cannot carry, and the composer says so rather than letting the
   * turn send and the agent ask.
   *
   * Derived on the server from the tool's own required arguments, never authored here.
   */
  readonly needs?: "file" | "skill";
}

/** A category and the tools in it, in display order. */
export interface ToolCatalogGroup {
  readonly category: string;
  readonly entries: readonly ToolCatalogEntry[];
}

/**
 * Group by the registry's own category; a second taxonomy here would drift.
 * Order follows first appearance, so the host's ordering decides.
 */
export function groupToolsByCategory(
  entries: readonly ToolCatalogEntry[],
): readonly ToolCatalogGroup[] {
  const order: string[] = [];
  const byCategory = new Map<string, ToolCatalogEntry[]>();

  for (const entry of entries) {
    const bucket = byCategory.get(entry.category);
    if (bucket === undefined) {
      order.push(entry.category);
      byCategory.set(entry.category, [entry]);
      continue;
    }
    bucket.push(entry);
  }

  return order.map((category) => ({
    category,
    entries: byCategory.get(category) ?? [],
  }));
}

/**
 * Matches id, name, summary and keywords, in any keyboard layout. Name alone is
 * not enough: a user with a recording types "voice", which `transcribe_audio`
 * does not contain.
 *
 * Matching and ordering read the same score, so a row can never rank above
 * another it does not also out-match.
 */
export function toolMatchesQuery(entry: ToolCatalogEntry, query: string): boolean {
  return scoreTool(entry, query) > 0;
}

/**
 * The catalogue narrowed to a query, ranked, grouped for display.
 *
 * Ranking runs BEFORE grouping and orders entries within each group; the groups
 * themselves keep the registry's order. Sorting groups by their best hit would
 * move a heading up and down as the user types, and a category that jumps is
 * harder to scan than one that stays put.
 *
 * Sort is stable on equal scores, so an empty query — where every entry scores
 * alike — leaves the registry's order untouched.
 */
export function filterToolCatalogue(
  entries: readonly ToolCatalogEntry[],
  query: string,
): readonly ToolCatalogGroup[] {
  const scored = entries
    .map((entry) => ({ entry, score: scoreTool(entry, query) }))
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score);

  return groupToolsByCategory(scored.map((row) => row.entry));
}
