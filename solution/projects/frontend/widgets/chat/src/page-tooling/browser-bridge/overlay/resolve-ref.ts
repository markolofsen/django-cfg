/**
 * Resolve a CST ref id to a live DOM element.
 *
 * The page-snapshot engine assigns each interactive element a ref
 * (`@e4`) during capture and keeps a `ref → element` registry. When the
 * AI returns a `point` directive citing a ref, the chat resolves it
 * back through that registry.
 *
 * A ref that no longer resolves is "stale" — the element was removed or
 * the user navigated away. Callers treat a null result as stale.
 *
 * The registry resolves each ref with a live-DOM query, so a ref
 * survives React recreating nodes between capture and directive
 * application. The `isConnected` check below is a defensive backstop —
 * a live query already returns connected elements.
 */

import type { CSTRefId } from './types';

/**
 * Minimal shape of a snapshot ref registry — `resolve(ref)` returns the
 * element or null. Structurally compatible with the page-snapshot
 * engine's `RefRegistry` without importing it (keeps the highlight
 * module decoupled from the capture engine internals).
 */
export interface RefResolver {
  resolve(ref: CSTRefId): HTMLElement | null;
}

/**
 * Resolve a batch of refs to elements, dropping the ones that no longer
 * exist. Returns pairs so the caller keeps the ref↔element association.
 */
export function resolveRefs(
  refs: CSTRefId[],
  resolver: RefResolver | null,
): Array<{ ref: CSTRefId; element: HTMLElement }> {
  if (!resolver) return [];
  const out: Array<{ ref: CSTRefId; element: HTMLElement }> = [];
  for (const ref of refs) {
    const element = resolver.resolve(ref);
    if (element && element.isConnected) {
      out.push({ ref, element });
    }
  }
  return out;
}
