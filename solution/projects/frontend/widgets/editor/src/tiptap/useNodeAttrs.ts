'use client';

/**
 * `useNodeAttrs` — the single write-back seam every interactive block NodeView
 * uses to persist UI changes back into the document (→ TipTap node attrs →
 * markdown round-trip).
 *
 * A NodeView is normally READ-ONLY: it renders `node.attrs` but has no path to
 * push a user action (drag a pin, toggle a basemap) back into the node. This
 * hook wraps TipTap's `updateAttributes` so an interactive component can do:
 *
 *   const { attrs, patch } = useNodeAttrs<MapBlockPayload>(props);
 *   // …on drag-end:
 *   patch({ markers: nextMarkers });
 *
 * and the new attrs land in the document — `getMarkdown()` then serialises the
 * updated payload.
 *
 * ## API
 *
 * - `attrs` — `props.node.attrs` typed as `T`. The current committed payload.
 * - `patch(next)` — commit a partial attr update IMMEDIATELY. `updateAttributes`
 *   is a single ProseMirror transaction, so this is cheap; use it for DISCRETE
 *   edits (drag-END, add/remove pin, basemap pick) — which is the recommended
 *   design: the caller fires `patch` only when a value is final, never per
 *   drag-frame, so no transaction spam.
 * - `patchDebounced(next, ms?)` — coalesce HIGH-FREQUENCY updates (a live edit
 *   firing many times: text input, a continuous slider). Rapid calls collapse
 *   into one trailing transaction after `ms` of quiet (default 250ms). Pending
 *   patches are MERGED so partial fields accumulate. Auto-flushes on unmount so
 *   the last edit is never lost.
 * - `flush()` — commit any pending debounced patch immediately (e.g. on blur).
 *
 * Pure + reusable: no editor-specific coupling, only the `NodeViewProps`
 * contract (`node`, `updateAttributes`). Node attrs stay plain-JSON
 * serializable — pass only JSON-safe values through `patch`.
 */

import { useCallback, useEffect, useMemo, useRef } from 'react';
import type { NodeViewProps } from '@tiptap/react';

/** Default debounce window (ms) for `patchDebounced`. */
const DEFAULT_DEBOUNCE_MS = 250;

export interface UseNodeAttrsResult<T extends Record<string, unknown>> {
  /** The node's current committed attrs, typed as `T`. */
  attrs: T;
  /** Commit a partial attr update immediately (one transaction). */
  patch: (next: Partial<T>) => void;
  /**
   * Commit a partial attr update on a trailing debounce; rapid calls merge
   * into a single transaction. For live/high-frequency edits.
   */
  patchDebounced: (next: Partial<T>, ms?: number) => void;
  /** Flush any pending debounced patch now (e.g. on blur). */
  flush: () => void;
}

/**
 * Two-way binding between a NodeView's UI and its node attrs.
 *
 * @param props The `NodeViewProps` TipTap hands the React NodeView component.
 */
export function useNodeAttrs<T extends Record<string, unknown>>(
  props: NodeViewProps,
): UseNodeAttrsResult<T> {
  const { node, updateAttributes } = props;
  const attrs = node.attrs as T;

  // Keep `updateAttributes` reachable from the debounce timer without making
  // the debounced callback re-create on every render (it can change identity).
  const updateRef = useRef(updateAttributes);
  updateRef.current = updateAttributes;

  // Pending merged patch + its timer, held across renders.
  const pendingRef = useRef<Partial<T> | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const flush = useCallback(() => {
    if (timerRef.current != null) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    const pending = pendingRef.current;
    if (pending) {
      pendingRef.current = null;
      updateRef.current(pending);
    }
  }, []);

  const patch = useCallback(
    (next: Partial<T>) => {
      // A discrete edit supersedes any queued debounced patch: merge the
      // pending fields in, then commit the lot as one transaction.
      const pending = pendingRef.current;
      if (timerRef.current != null) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      pendingRef.current = null;
      updateRef.current(pending ? { ...pending, ...next } : next);
    },
    [],
  );

  const patchDebounced = useCallback(
    (next: Partial<T>, ms: number = DEFAULT_DEBOUNCE_MS) => {
      // Merge so partial fields accumulate across rapid calls.
      pendingRef.current = { ...(pendingRef.current ?? {}), ...next };
      if (timerRef.current != null) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        timerRef.current = null;
        const pending = pendingRef.current;
        pendingRef.current = null;
        if (pending) updateRef.current(pending);
      }, ms);
    },
    [],
  );

  // Never drop the last edit: flush on unmount.
  useEffect(() => () => flush(), [flush]);

  return useMemo(
    () => ({ attrs, patch, patchDebounced, flush }),
    [attrs, patch, patchDebounced, flush],
  );
}
