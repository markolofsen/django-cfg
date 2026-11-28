/**
 * Detecting a trigger (`@machine`, `/command`) from text and a caret.
 *
 * PURE, and that is the point rather than a style preference. The editor
 * decision is "textarea first, Tiptap on a named trigger", so the surface
 * WILL be replaced. Keeping detection as a function of
 * (text, caret) means the swap replaces rendering only — this logic, and its
 * tests, survive untouched.
 *
 * Form taken from assistant-ui's `detectTrigger` (MIT, 37 lines, zero imports),
 * which scans backwards from the caret and stops at whitespace. One deliberate
 * difference is documented at `allowSpaces` below.
 */

export interface TriggerMatch {
  /** Text typed after the trigger character, up to the caret. */
  readonly query: string;
  /** Index of the trigger character in the source text. */
  readonly offset: number;
}

export interface DetectOptions {
  /**
   * Let the query contain spaces, up to `maxWords`.
   *
   * OFF by default, matching the reference. Turned ON for machine mentions,
   * because our machine names legitimately contain spaces ("Mark's MacBook")
   * and a strict scan closes the menu at the first one — mid-name, exactly when
   * the user still needs it.
   *
   * The bound is what keeps that from being a regression: without it, an
   * unmatched `@` earlier in a paragraph keeps matching for the rest of the
   * message and the menu never closes.
   */
  readonly allowSpaces?: boolean;
  /** Max whitespace-separated words in the query when `allowSpaces`. */
  readonly maxWords?: number;
}

const WHITESPACE = /\s/u;

const DEFAULT_MAX_WORDS = 3;

/**
 * Find an active trigger at the caret, or null.
 *
 * The trigger must be preceded by whitespace or start the text, so an email
 * address never opens a mention menu — the case that makes a naive `indexOf`
 * unusable.
 */
export function detectTrigger(
  text: string,
  triggerChar: string,
  caret: number,
  options: DetectOptions = {},
): TriggerMatch | null {
  if (triggerChar === "") return null;

  // Only text up to the caret can be part of the query: characters after it
  // belong to a word the user already finished typing.
  const upToCaret = text.slice(0, Math.max(0, Math.min(caret, text.length)));
  const { allowSpaces = false, maxWords = DEFAULT_MAX_WORDS } = options;

  // Counts GAPS between words, not whitespace characters. A run of spaces is
  // one gap: counting characters made `@a  b  c  d` close while `@a b c d`
  // stayed open, so how the user spaced their text decided where the menu gave
  // up. `wasSpace` collapses the run — the scan walks backwards, so this is the
  // character to the RIGHT of the one being read.
  let gaps = 0;
  let wasSpace = false;

  for (let i = upToCaret.length - 1; i >= 0; i--) {
    const char = upToCaret[i] ?? "";

    if (WHITESPACE.test(char)) {
      // A newline always ends a query, even with allowSpaces: a mention cannot
      // span a paragraph, and letting it would keep the menu open forever.
      if (!allowSpaces || char === "\n") return null;
      if (!wasSpace) {
        gaps += 1;
        // N words are separated by N-1 gaps, so the bound is `>=`. With `>` a
        // `maxWords: 3` query keeps matching through a FOURTH word, and the
        // menu stays open across an entire sentence typed after a completed
        // mention.
        if (gaps >= maxWords) return null;
      }
      wasSpace = true;
      continue;
    }
    wasSpace = false;

    if (!upToCaret.startsWith(triggerChar, i)) continue;

    // Preceded by whitespace, or at the very start. Without this,
    // "mail@example.com" opens a mention menu on every keystroke.
    const preceding = i > 0 ? (upToCaret[i - 1] ?? "") : "";
    if (i > 0 && !WHITESPACE.test(preceding)) continue;

    return { query: upToCaret.slice(i + triggerChar.length), offset: i };
  }

  return null;
}

/**
 * Replace an active trigger with a resolved value.
 *
 * Lives beside detection because the two share one definition of where the
 * query starts and ends. Splitting them is how an off-by-one appears the day
 * the trigger becomes two characters long.
 *
 * The replacement REPLACES the trigger character, it does not follow it — the
 * slice starts at `match.offset`, which is the `@` itself. That is deliberate,
 * because the caller's serializer decides the final form and may need the `@`
 * inside a label (`[@name](url)`) rather than outside it. Restoring the trigger
 * here would double it for every such caller.
 */
export function applyTrigger(
  text: string,
  match: TriggerMatch,
  caret: number,
  replacement: string,
): { readonly text: string; readonly caret: number } {
  const end = Math.max(0, Math.min(caret, text.length));
  // A trailing space is part of the replacement, not a separate edit: without
  // it the caret sits against the inserted name and the next character types
  // straight into a completed mention.
  const insert = `${replacement} `;

  return {
    text: text.slice(0, match.offset) + insert + text.slice(end),
    caret: match.offset + insert.length,
  };
}
