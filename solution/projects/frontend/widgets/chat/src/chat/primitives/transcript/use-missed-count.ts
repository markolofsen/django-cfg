import { useMemo, useRef } from "react";

import { MissedCount, missedRows } from "../../core/screen";
import { useChatStore } from "../../store";

/**
 * How many replies arrived while the reader was scrolled away.
 *
 * Reads roles imperatively off the store instead of subscribing to the message
 * array. A `useMessages()` selector would re-render the transcript on every
 * token — the exact cost the `useMessageIds()` / `useMessage(id)` split exists
 * to avoid (`store/hooks.ts`). Here it is free: the count can only change when
 * `ids` changes, and the transcript already re-renders then.
 *
 * @param ids the transcript's message ids, in order
 * @param pinned whether the viewport is following the bottom
 */
export function useMissedCount(ids: readonly string[], pinned: boolean): number | null {
  const store = useChatStore();
  const counter = useRef<MissedCount | null>(null);
  counter.current ??= new MissedCount();

  return useMemo(() => {
    const missed = counter.current;
    if (missed === null) return null;
    const byId = store.getState().transcript.byId;
    missed.observe(pinned, missedRows(ids, byId));
    return missed.value();
  }, [store, ids, pinned]);
}
