/**
 * Redaction pattern catalog — secret / PII value patterns.
 *
 * Applied to string values (input values, static text) — these scrub
 * sensitive substrings out of otherwise-keepable text. A separate
 * heuristic layer (heuristics.ts) drops whole fields by element shape.
 *
 */

import { validateLuhn } from './luhn';

/** A named value-redaction rule. */
export interface RedactionPattern {
  /** Identifier, surfaced in the audit report. */
  name: string;
  /** Matcher applied to string values (must be global for replaceAll). */
  test: RegExp;
  /**
   * Optional extra check on a match before redacting — used to avoid
   * false positives (e.g. Luhn for cards). Return true to redact.
   */
  confirm?: (match: string) => boolean;
}

/** Placeholder a matched secret/PII substring is replaced with. */
export function patternToken(name: string): string {
  return `‹redacted:${name}›`;
}

/**
 * The catalog. Order matters — more specific patterns first so a token
 * is not partially eaten by a broader rule.
 */
export const REDACTION_PATTERNS: RedactionPattern[] = [
  {
    // JWT — three base64url segments.
    name: 'jwt',
    test: /\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b/g,
  },
  {
    // Bearer / authorization header value.
    name: 'bearer-token',
    test: /\bBearer\s+[A-Za-z0-9\-._~+/]{16,}=*/gi,
  },
  {
    // Common API-key prefixes (Stripe, OpenAI, GitHub, generic sk-/pk-).
    name: 'api-key',
    test: /\b(?:sk|pk|rk|ghp|gho|github_pat|xox[baprs])[-_][A-Za-z0-9-_]{16,}\b/g,
  },
  {
    // AWS access key id.
    name: 'aws-key',
    test: /\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/g,
  },
  {
    // Email address (RFC-5322-ish, pragmatic).
    name: 'email',
    test: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
  },
  {
    // IBAN — country code + check digits + up to 30 alphanumerics.
    name: 'iban',
    test: /\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b/g,
  },
  {
    // Credit-card-shaped digit runs — Luhn-confirmed to avoid eating
    // order numbers and other long IDs.
    name: 'credit-card',
    test: /\b(?:\d[ -]?){13,19}\b/g,
    confirm: validateLuhn,
  },
  {
    // Phone number — must look like a phone, not just a long digit run.
    // Requires either a leading "+" or separators (space/()/-), and a
    // digit count in the 7–15 range. A bare 16-digit string is an ID,
    // not a phone, and must survive.
    name: 'phone',
    test: /\+?\d[\d\s().-]{5,}\d/g,
    confirm: (m) => {
      const digits = m.replace(/\D/g, '');
      if (digits.length < 7 || digits.length > 15) return false;
      const hasPlus = m.trimStart().startsWith('+');
      const hasSeparators = /[\s().-]/.test(m);
      return hasPlus || hasSeparators;
    },
  },
];

/**
 * Redact every pattern match within a string.
 * Returns the scrubbed string and the names of patterns that fired.
 */
export function redactPatterns(value: string): {
  value: string;
  matched: string[];
} {
  let result = value;
  const matched: string[] = [];

  for (const pattern of REDACTION_PATTERNS) {
    // Fresh lastIndex each pattern.
    pattern.test.lastIndex = 0;
    result = result.replace(pattern.test, (match) => {
      if (pattern.confirm && !pattern.confirm(match)) return match;
      if (!matched.includes(pattern.name)) matched.push(pattern.name);
      return patternToken(pattern.name);
    });
  }

  return { value: result, matched };
}
