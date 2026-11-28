export type Listener = () => void;

/**
 * Who gets told, and how narrowly.
 *
 * Split out of `store.ts` because it is the one part that touches no state at
 * all: it holds two sets of callbacks and decides which of them to wake. The
 * store owns WHEN a transition happens; this owns WHO hears about it.
 *
 * Per-message subscription is the load-bearing part, not an optimisation. A
 * transcript that re-renders every row on every token is the difference between
 * a chat that feels instant and one that stutters at fifty messages — and it
 * cannot be retrofitted, because it decides the shape of the selectors.
 */
export interface Subscribers {
  /** Wake the whole-store listeners, plus the rows named in `changed`. */
  readonly notify: (changed: Iterable<string>) => void;
  /** Subscribe to any change. Returns the unsubscribe. */
  readonly subscribe: (listener: Listener) => () => void;
  /** Subscribe to ONE message's changes. Returns the unsubscribe. */
  readonly subscribeMessage: (id: string, listener: Listener) => () => void;
}

export function createSubscribers(): Subscribers {
  const listeners = new Set<Listener>();
  const perMessage = new Map<string, Set<Listener>>();

  return {
    notify(changed) {
      for (const listener of listeners) listener();
      for (const id of changed) {
        const set = perMessage.get(id);
        if (set === undefined) continue;
        for (const listener of set) listener();
      }
    },

    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },

    subscribeMessage(id, listener) {
      const set = perMessage.get(id) ?? new Set<Listener>();
      set.add(listener);
      perMessage.set(id, set);
      return () => {
        set.delete(listener);
        // Dropped when the last listener for that id leaves, so a long session
        // does not accumulate an empty Set per message ever rendered.
        if (set.size === 0) perMessage.delete(id);
      };
    },
  };
}
