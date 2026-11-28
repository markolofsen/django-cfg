/**
 * When does an arrow key walk the prompt ladder, and when does it move the
 * caret?
 *
 * Pure — a function of the buffer, the caret and what recall last wrote — so the
 * whole interaction is testable without an editor. The surface is meant to be
 * swappable (textarea → Tiptap) without retesting the rules.
 *
 * ## The rule, and where it comes from
 *
 * Recall used to require a COMPLETELY empty composer. That made ArrowUp a dead
 * key in any multi-line draft and left the down direction nowhere to go. The
 * shells settled this decades ago with a boundary test, and zsh's
 * `up-line-or-beginning-search` is the cheapest correct form: it asks whether
 * the text LEFT OF THE CARET contains a newline rather than computing a row
 * index. That is `atFirstLine`.
 *
 * ## The soft-wrap limit, stated rather than discovered
 *
 * One long line that WRAPS across three visual rows is ONE logical line here, so
 * ArrowUp navigates instead of moving up a visual row. Doing better needs
 * `coordsAtPos` pixel geometry and a live DOM, which this seam does not have —
 * and a second editor-specific path is a worse trade than a named limit.
 *
 * Not hypothetical: it is the live complaint against Claude Code
 * (anthropics/claude-code#63670), whose docs promise a visual-row rule its
 * shipped build does not implement. We promise the logical-line rule and
 * implement exactly that, and the story says so.
 */

/**
 * Caret position within the composer buffer.
 *
 * A collapsed caret has `start === end`. A selection never navigates.
 */
export interface ComposerCaret {
  readonly start: number;
  readonly end: number;
}

/**
 * True when nothing in the buffer sits above the caret — the top of the ladder.
 *
 * A selection is never a boundary: Up with text selected means "extend or
 * collapse", and hijacking it destroys a selection the user is building.
 * DevTools takes the same position.
 */
export function atFirstLine(value: string, caret: ComposerCaret | null): boolean {
  if (value === "") return true;
  if (caret === null || caret.start !== caret.end) return false;
  return !value.slice(0, caret.start).includes("\n");
}

/** True when nothing in the buffer sits below the caret — the bottom rung. */
export function atLastLine(value: string, caret: ComposerCaret | null): boolean {
  if (value === "") return true;
  if (caret === null || caret.start !== caret.end) return false;
  return !value.slice(caret.end).includes("\n");
}

/**
 * May an arrow press navigate at all, whatever the caret says?
 *
 * Only while the buffer is still recall's own: empty, or byte-identical to what
 * recall last wrote. The moment the user types a character the buffer is theirs
 * and arrows only move the caret.
 *
 * Taken from Codex's gate, and it has a second consequence worth naming: a
 * non-empty buffer never navigates, so there is no buffer for a prefix filter to
 * read. zsh/fish-style prefix search and this rule are mutually exclusive by
 * construction — prefix search is off the table until something like `Ctrl+R`
 * is wired instead.
 */
export function bufferIsRecallOwned(value: string, lastRecalled: string | null): boolean {
  if (value === "") return true;
  return lastRecalled !== null && value === lastRecalled;
}
