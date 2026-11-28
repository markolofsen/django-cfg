/**
 * UI directives — how the AI points at the user's screen.
 *
 * The chat response can carry directives; for now the only one is
 * `point` (highlight / focus an element). The union is a discriminated
 * type so a future write-style directive (e.g. `fill`) can be added
 * without breaking older clients — unknown `type`s are simply ignored.
 */

import type { CSTRefId } from './types';

/**
 * Point at an element: highlight and/or focus it. Read-only — neither
 * changes the user's data.
 */
export interface PointDirective {
  type: 'point';
  /** CST ref of the target element. */
  ref: CSTRefId;
  /** Draw the highlight overlay (default: true). */
  highlight?: boolean;
  /** Call element.focus() once visible (default: false). */
  focus?: boolean;
  /** Optional short caption shown beside the highlight. */
  label?: string;
}

/**
 * The directive union. MVP ships `point` only.
 *
 * Level 3 (future, NOT built) would add:
 *   | { type: 'fill'; ref: CSTRefId; value: string }
 *
 * Any consumer must `switch` on `type` and ignore unknown variants —
 * never throw — so an older client meeting a newer directive is safe.
 */
export type UIDirective = PointDirective;

/** Carried in the structured side-channel of the SSE response. */
export interface ChatResponseMeta {
  directives?: UIDirective[];
}

/** Type guard: is this a `point` directive. */
export function isPointDirective(d: UIDirective): d is PointDirective {
  return d.type === 'point';
}
