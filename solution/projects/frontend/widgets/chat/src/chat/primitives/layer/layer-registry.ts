import { pushLayer, reconcileLayers, releaseLayer, settleLayers, type LayerEntry } from "../../core/screen";

/**
 * Open layers as browser-history entries, so the phone's Back gesture closes the top layer instead of leaving the page.
 * One entry per layer; `popstate` closes whatever the history left behind; a layer closed from inside has its entry
 * removed after a short wait (a layer that opens right after keeps the stack consistent).
 */
let entries: LayerEntry[] = [];
const closers = new Map<string, () => void>();
let listening = false;
let timer = 0;

const SETTLE_MS = 60;
const KEY = "__layer";
const DEPTH = "__depth";

function onPop() {
  const state = window.history.state as Record<string, unknown> | null;
  const depth = typeof state?.[DEPTH] === "number" ? (state[DEPTH] as number) : 0;
  const next = reconcileLayers(entries, depth);
  entries = next.entries;
  next.closed.reverse().forEach((id) => closers.get(id)?.());
}

/** The layer depth stored in the entry the page is on now; 0 when the page has moved on to an entry of its own (a navigation). */
function currentDepth(): number {
  const state = window.history.state as Record<string, unknown> | null;
  return typeof state?.[DEPTH] === "number" ? (state[DEPTH] as number) : 0;
}

function flush() {
  timer = 0;
  const next = settleLayers(entries, currentDepth());
  entries = next.entries;
  if (next.pop > 0) window.history.go(-next.pop);
}

/** Registers an open layer; returns the call to make when it closes. `onBack` runs when the history leaves it. */
export function registerLayer(id: string, onBack: () => void): () => void {
  if (!listening) {
    window.addEventListener("popstate", onPop);
    listening = true;
  }
  entries = pushLayer(entries, id);
  closers.set(id, onBack);
  // Keep the page's own history state: a router that stored something there must still find it.
  const own = (window.history.state ?? {}) as Record<string, unknown>;
  window.history.pushState({ ...own, [KEY]: id, [DEPTH]: entries.length }, "");
  return () => {
    closers.delete(id);
    entries = releaseLayer(entries, id);
    window.clearTimeout(timer);
    timer = window.setTimeout(flush, SETTLE_MS);
  };
}
