/**
 * Heuristic redaction — drop a whole field's value by element shape.
 *
 * Where patterns.ts scrubs sensitive substrings, this decides that an
 * entire field is sensitive (a password input, an element named
 * `*token*`/`*secret*`) and its value must never be captured at all.
 *
 * Safe-by-default: an un-annotated page is still covered — heuristics
 * do not depend on developers adding `data-ai-redact`.
 *
 */

/**
 * Attribute-name / token pattern that marks a field as sensitive.
 * Tested against id, name, class, autocomplete.
 */
const SENSITIVE_NAME_RE =
  /(^|[\s_-])(password|passwd|pwd|secret|token|api[-_]?key|apikey|auth|bearer|cvv|cvc|card[-_]?number|cc[-_]?num|ssn|sin|tax[-_]?id|private[-_]?key|stripe|client[-_]?secret|access[-_]?key)([\s_-]|$)/i;

/** autocomplete values that mark a sensitive field. */
const SENSITIVE_AUTOCOMPLETE: ReadonlySet<string> = new Set([
  'current-password',
  'new-password',
  'cc-number',
  'cc-csc',
  'one-time-code',
]);

/** Why a heuristic fired (used for the audit reason / token kind). */
export type HeuristicKind = 'password' | 'sensitive-name' | 'autocomplete';

/**
 * Decide whether an element's value must be fully redacted by shape.
 * Returns the heuristic kind, or null if the element is not sensitive.
 */
export function heuristicRedactKind(el: Element): HeuristicKind | null {
  // A password input — never capture its value.
  if (el instanceof HTMLInputElement && el.type === 'password') {
    return 'password';
  }

  // autocomplete hint.
  const autocomplete = el.getAttribute('autocomplete')?.toLowerCase();
  if (autocomplete && SENSITIVE_AUTOCOMPLETE.has(autocomplete)) {
    return 'autocomplete';
  }

  // id / name / class token pattern.
  const tokens = [
    el.id,
    el.getAttribute('name') ?? '',
    typeof el.className === 'string' ? el.className : '',
  ].join(' ');
  if (tokens.trim() && SENSITIVE_NAME_RE.test(tokens)) {
    return 'sensitive-name';
  }

  return null;
}

/**
 * Does this element (or an ancestor) carry `data-ai-redact` — an
 * explicit developer instruction to drop the whole subtree.
 */
export function hasRedactAnnotation(el: Element): boolean {
  return el.closest('[data-ai-redact]') !== null;
}

/**
 * Does this element carry `data-ai-include` — an explicit override that
 * forces a heuristically-blocked but known-safe value to be kept.
 */
export function hasIncludeAnnotation(el: Element): boolean {
  return el.hasAttribute('data-ai-include');
}
