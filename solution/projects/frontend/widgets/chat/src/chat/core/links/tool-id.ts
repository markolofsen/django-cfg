import { parse as parseMentionUrl } from "./scheme";

/**
 * `app://tool/<id>` — the link a picked tool becomes in the outbound text.
 *
 * Unlike a named correspondent there is no `@token` preprocess step here: the
 * COMPOSER writes the link itself, so the id never has to be recovered from
 * prose. This module owns only the reading half.
 */

/**
 * Extract the tool id from a `app://tool/<id>` href, or null for any other
 * shape. Uses the single-sourced `core/links` parser so the scheme stays in
 * lock-step with Go.
 *
 * A bare `app://tool` parses but names no tool, and returns null here — the
 * caller must treat "no id" and "not a tool link" the same way, since neither
 * identifies anything a chip could stand for.
 */
export function extractToolId(href: string | undefined): string | null {
  if (!href) return null;
  const r = parseMentionUrl(href);
  if (!r.ok) return null;
  if (r.parsed.kind !== "tool") return null;
  return r.parsed.toolID || null;
}
