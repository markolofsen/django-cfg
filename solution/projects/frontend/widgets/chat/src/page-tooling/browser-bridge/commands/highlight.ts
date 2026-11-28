'use client';

/**
 * Spotlight commands — `highlight`, `focus`, `clear`.
 *
 * All three drive the directive bus the AI uses, so the overlay reacts
 * identically whether the source is an SSE event or a console call.
 */

import { log } from '../logger';
import { pushDirectives, clearDirectives } from '../directive-bus';
import { registerBridgeCommand } from '../registry';
import type { CSTRefId, PointDirective } from '../overlay/types';

/** Coerce loose console input ("@e4" or ["@e4","@e5"]) into a ref list. */
function toRefList(input: CSTRefId | CSTRefId[]): CSTRefId[] {
  return Array.isArray(input) ? input : [input];
}

/**
 * highlight — spotlight one or more elements by CST ref.
 * Drives the same directive bus the AI uses, so the overlay reacts
 * identically whether the source is an SSE event or a console call.
 */
export const highlight = registerBridgeCommand({
  name: 'highlight',
  description: 'highlight(refs, opts?) — spotlight element(s) by CST ref',
  mutates: false,
  run: (
    refs: CSTRefId | CSTRefId[],
    opts?: { focus?: boolean; label?: string },
  ): { dispatched: number } => {
    const list = toRefList(refs);
    const directives: PointDirective[] = list.map((ref) => ({
      type: 'point',
      ref,
      focus: opts?.focus,
      label: opts?.label,
    }));
    log.info('bridge.highlight', { refs: list, opts });
    pushDirectives(directives);
    return { dispatched: directives.length };
  },
});

/**
 * focus — spotlight a single element AND move keyboard focus into it.
 * A thin convenience over `highlight` with `focus: true`.
 */
export const focus = registerBridgeCommand({
  name: 'focus',
  description: 'focus(ref, label?) — highlight an element and focus it',
  mutates: false,
  run: (ref: CSTRefId, label?: string): { dispatched: number } => {
    log.info('bridge.focus', { ref, label });
    pushDirectives([{ type: 'point', ref, focus: true, label }]);
    return { dispatched: 1 };
  },
});

/** clear — dismiss any active highlight overlay. */
export const clear = registerBridgeCommand({
  name: 'clear',
  description: 'clear() — remove the active highlight overlay',
  mutates: false,
  run: (): void => {
    log.info('bridge.clear');
    clearDirectives();
  },
});
