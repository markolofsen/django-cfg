// How well a catalogue entry answers a query.
//
// May import: ./catalogue, ./layout.

import type { ToolCatalogEntry } from "./catalogue";
import { queryLayoutForms } from "./layout";

/**
 * Field weights. A summary hit is often incidental: "gen" matches "the agent's
 * browser", which is how an unranked filter put Browser navigate first.
 */
const NAME = 1000;
const ID = 800;
const KEYWORD = 600;
const SUMMARY = 200;

/** A prefix hit beats one mid-word: "gen" means Generate before Regenerate. */
const PREFIX_BONUS = 100;

/** Every layout form after the first is a guess about what the user meant. */
const TRANSLITERATED_PENALTY = 50;

function fieldScore(haystack: string, needle: string, weight: number): number {
  const at = haystack.toLowerCase().indexOf(needle);
  if (at < 0) return 0;
  return weight + (at === 0 ? PREFIX_BONUS : 0);
}

function scoreForNeedle(entry: ToolCatalogEntry, needle: string): number {
  const keywords = (entry.keywords ?? []).reduce(
    (best, keyword) => Math.max(best, fieldScore(keyword, needle, KEYWORD)),
    0,
  );
  // Best field, not the sum: summing lets a long summary outrank an exact name.
  return Math.max(
    fieldScore(entry.name, needle, NAME),
    fieldScore(entry.id, needle, ID),
    keywords,
    fieldScore(entry.summary, needle, SUMMARY),
  );
}

/**
 * 0 when the entry does not match at all; higher is more relevant.
 *
 * An empty query scores every entry equally, so the caller's own order (the
 * registry's) survives — the menu at rest is not a search result.
 */
export function scoreTool(entry: ToolCatalogEntry, query: string): number {
  const forms = queryLayoutForms(query);
  if (forms.length === 0) return 1;

  let best = 0;
  for (const [index, form] of forms.entries()) {
    const score = scoreForNeedle(entry, form.toLowerCase());
    if (score === 0) continue;
    best = Math.max(best, score - (index === 0 ? 0 : TRANSLITERATED_PENALTY));
  }
  return best;
}
