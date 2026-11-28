'use client';

/**
 * Highlight overlay — how a `point` directive is drawn.
 *
 * Resolves CST refs to live elements, tracks their geometry, and draws
 * an SVG-mask spotlight over them. Read-only: it highlights and
 * optionally focuses elements, never changes the user's data.
 */

export { HighlightOverlay, type HighlightOverlayProps } from './highlight-overlay';
export { SpotlightCanvas, type SpotlightCanvasProps } from './spotlight-canvas';
export { useHighlightTargets } from './use-highlight-targets';
export { resolveRefs, type RefResolver } from './resolve-ref';
export {
  waitForVisible,
  type WaitForVisibleOptions,
} from './wait-for-visible';
export type {
  PointDirective,
  HighlightTarget,
  SpotlightRect,
  CSTRefId,
} from './types';
