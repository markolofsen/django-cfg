/**
 * Redaction entry point — scrub secrets / PII from a captured value.
 *
 * Two layers, applied at traverse time:
 *   1. heuristic — a whole field redacted by element shape
 *      (password input, `*token*`-named field).
 *   2. pattern — sensitive substrings scrubbed out of otherwise-kept
 *      text (JWT, API keys, emails, Luhn-validated cards, …).
 *
 * Safe-by-default: an un-annotated page is still covered. `data-ai-redact`
 * (drop subtree) is handled in the walk; `data-ai-include` overrides the
 * heuristic layer for a known-safe value.
 *
 */

import type { RedactContext, RedactValue } from '../capture/walk';
import type { RedactionAuditor, RedactionReason } from './audit';
import {
  hasIncludeAnnotation,
  heuristicRedactKind,
} from './heuristics';
import { redactPatterns } from './patterns';

export type { RedactionAuditReport, RedactionReason } from './audit';
export { RedactionAuditor } from './audit';

/** Token substituted for a fully-redacted value. */
export function redactionToken(kind: string): string {
  return `‹redacted:${kind}›`;
}

/**
 * Build a redaction function bound to an auditor.
 *
 * The returned `RedactValue` is the hook the DOM walk calls for every
 * captured input value and text run.
 */
export function createRedactor(auditor: RedactionAuditor): RedactValue {
  return (value: string, context: RedactContext): string => {
    auditor.markScanned();
    if (!value) return value;

    const { element, kind, ref } = context;

    // Layer 1 — heuristic field-level redaction (input values only;
    // static text has no single owning field shape).
    if (kind === 'value') {
      const heuristic = heuristicRedactKind(element);
      if (heuristic && !hasIncludeAnnotation(element)) {
        auditor.log({
          elementRole: element.tagName.toLowerCase(),
          triggerReason: 'heuristic',
          assignedRef: ref,
        });
        return redactionToken(heuristic);
      }
    }

    // Layer 2 — pattern substring redaction.
    const { value: scrubbed, matched } = redactPatterns(value);
    if (matched.length > 0) {
      const reason: RedactionReason = 'regex';
      for (const _name of matched) {
        auditor.log({
          elementRole: element.tagName.toLowerCase(),
          triggerReason: reason,
          assignedRef: ref,
        });
      }
      return scrubbed;
    }

    return value;
  };
}
