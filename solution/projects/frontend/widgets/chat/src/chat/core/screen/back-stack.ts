/** One browser-history entry pushed by an open layer. `depth` is stored in the entry's state so a popstate tells how many entries are gone. */
export interface Entry {
  id: string;
  depth: number;
  /** The layer is still open. A layer closed from inside leaves a dead entry until `settle` removes it. */
  live: boolean;
}

export function push(entries: Entry[], id: string): Entry[] {
  return [...entries, { id, depth: entries.length + 1, live: true }];
}

/** The layer closed by itself (button, Escape, overlay). */
export function release(entries: Entry[], id: string): Entry[] {
  return entries.map((entry) => (entry.id === id ? { ...entry, live: false } : entry));
}

/** History moved to `depth` (0 = the page): entries above it are gone; the live ones among them must close. */
export function reconcile(entries: Entry[], depth: number): { entries: Entry[]; closed: string[] } {
  return { entries: entries.filter((e) => e.depth <= depth), closed: entries.filter((e) => e.depth > depth && e.live).map((e) => e.id) };
}

/**
 * Dead entries on top of the stack are popped with one `history.go(-pop)`; dead ones under a live layer wait for it.
 *
 * `current` is the `depth` stored in the state of the history entry the page is on now (0: an entry that is not one of ours).
 * The pop is only right while the top layer entry is that entry. When the page navigated on top of it (a link or a
 * sign-in button inside the layer, then the layer unmounts), `go(-pop)` would undo the navigation and send the reader back
 * where they came from; the dead entries are then forgotten and left in the history.
 */
export function settle(entries: Entry[], current: number = entries.length): { entries: Entry[]; pop: number } {
  let end = entries.length;
  while (end > 0 && !entries[end - 1]?.live) end -= 1;
  const pop = entries.length - end;
  if (pop > 0 && current !== entries.length) return { entries: entries.slice(0, end), pop: 0 };
  return { entries: entries.slice(0, end), pop };
}
