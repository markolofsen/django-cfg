// Recently used tools, as data.
//
// May import: ./catalogue.

import type { ToolCatalogEntry } from "./catalogue";

/**
 * How many recents a user can hold in their head before the group stops being
 * a shortcut and becomes a second catalogue to read.
 */
export const RECENT_LIMIT = 5;

/** Most recent first, capped, no duplicates. */
export function rememberTool(recent: readonly string[], id: string): readonly string[] {
  return [id, ...recent.filter((known) => known !== id)].slice(0, RECENT_LIMIT);
}

export function forgetTool(recent: readonly string[], id: string): readonly string[] {
  return recent.filter((known) => known !== id);
}

/**
 * Recent ids resolved against the CURRENT catalogue, in recency order.
 *
 * A tool the host no longer registers drops out rather than rendering a row
 * that picks nothing. The stored list is not pruned — the tool may return.
 */
export function recentTools(
  entries: readonly ToolCatalogEntry[],
  recent: readonly string[],
): readonly ToolCatalogEntry[] {
  const byId = new Map(entries.map((entry) => [entry.id, entry]));
  const resolved: ToolCatalogEntry[] = [];
  for (const id of recent) {
    const entry = byId.get(id);
    if (entry !== undefined) resolved.push(entry);
  }
  return resolved;
}
