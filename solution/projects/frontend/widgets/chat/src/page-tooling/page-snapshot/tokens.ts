/**
 * Token estimation.
 *
 * A cheap heuristic — chars / 4.2 — good enough to drive budget
 * decisions client-side. The backend does the authoritative count.
 */

/** Average characters per token, empirically ~4.2 for mixed UI text. */
const CHARS_PER_TOKEN = 4.2;

/** Estimate the token count of a string. */
export function estimateTokens(text: string): number {
  if (!text) return 0;
  return Math.ceil(text.length / CHARS_PER_TOKEN);
}
