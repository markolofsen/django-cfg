/**
 * Types for the AI-driven highlight overlay.
 *
 * The assistant points at the page by CST ref id; the chat resolves
 * each ref to a live element and this overlay draws a spotlight on it.
 */

/** A CST ref id, e.g. "@e4". */
export type CSTRefId = `@e${number}`;

/** A `point` directive as received from the backend SSE stream. */
export interface PointDirective {
  type: 'point';
  /** CST ref of the target element. */
  ref: CSTRefId;
  /** Draw the highlight overlay (default: true). */
  highlight?: boolean;
  /** Move focus into the element once visible (default: false). */
  focus?: boolean;
  /** Optional short caption shown beside the highlight. */
  label?: string;
}

/**
 * One resolved highlight target — a directive whose ref was found in
 * the live DOM, paired with its element and measured rect.
 */
export interface HighlightTarget {
  /** The resolved DOM element. */
  element: HTMLElement;
  /** Measured bounding rect (viewport coords). */
  rect: DOMRect;
  /** Caption to render beside the highlight. */
  label?: string;
  /** Whether to move focus into the element. */
  focus: boolean;
}

/**
 * A geometry-only target the SVG renderer consumes — decoupled from the
 * DOM element so the renderer stays a pure presentational component.
 */
export interface SpotlightRect {
  rect: DOMRect;
  /** Extra px around the element. */
  padding: number;
  /** Corner radius. */
  radius: number;
}
