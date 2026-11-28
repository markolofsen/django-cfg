import { useCallback, useMemo, useSyncExternalStore } from "react";

import type { Draft } from "../../core/compose/outbound";
import type { QueuedPrompt } from "../../core/compose/queue";
import { useChatEvents, useChatStore } from "../hooks";

/**
 * React binding for the prompt queue.
 *
 * Thin, like `useMentions` and `useVoice`: the ordering and the empty rules live
 * in `core/compose/queue`, tested without a DOM. This subscribes.
 */

export interface UseQueueResult {
  readonly items: readonly QueuedPrompt[];
  readonly count: number;
  readonly remove: (id: string) => void;
  /** Replace a queued draft; editing it to empty removes the entry. */
  readonly edit: (id: string, draft: Draft) => void;
  /** Remove and return one queued draft, for editing it in the composer. */
  readonly take: (id: string) => Draft | undefined;
  /** Cut the current turn short and release this prompt now. */
  readonly sendNow: (id: string) => void;
}

export function useQueue(): UseQueueResult {
  const store = useChatStore();
  // Announced from here rather than from the store: the store is clock-free
  // pure core, and handing it the bus would give it a second way to notify
  // beside `notify` — one that carries no snapshot and nothing can replay.
  const events = useChatEvents();
  const queue = useSyncExternalStore(
    store.subscribe,
    useCallback(() => store.getState().queue, [store]),
  );

  // Keyed on the store alone, never on the queue — the defect fixed in
  // `use-mentions.ts`. A host putting `remove` in an effect's dependency array
  // would otherwise re-run it on every enqueue, forever.
  const actions = useMemo(
    () => ({
      remove: (id: string) => store.removeQueued(id),
      edit: (id: string, draft: Draft) => store.editQueued(id, draft),
      take: (id: string) => store.takeQueued(id),
      sendNow: (id: string) => {
        // Announced only when the prompt actually MOVED past a running turn.
        // With nothing in flight `sendQueuedNow` just sends it, and reporting a
        // promotion there would describe an interruption that never happened.
        const wasStreaming = store.getState().inFlight !== null;
        store.sendQueuedNow(id);
        if (wasStreaming) events.emit("queue:promoted", { id });
      },
    }),
    [store, events],
  );

  return useMemo(
    () => ({ items: queue.items, count: queue.items.length, ...actions }),
    [queue, actions],
  );
}
