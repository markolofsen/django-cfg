'use client';

import { useCallback, useSyncExternalStore } from 'react';

/**
 * Minimal imperative handle every text-editor surface implements so
 * an external tool (voice dictation, command palette, AI suggestion)
 * can read/write its text content without traversing React.
 *
 * Methods are optional so a host can register a partial handle
 * (e.g. only `getValue` + `setValue`), and the caller checks before use.
 */
export interface ComposerHandle {
  /** Move keyboard focus into the composer's editable surface. */
  focus: () => void;
  /** Move the caret to the very end of the input. */
  moveCursorToEnd?: () => void;
  /** Read the current draft text. Voice dictation anchors partial
   *  transcripts onto the user's already-typed prefix via this. */
  getValue?: () => string;
  /** Replace the current draft text. Voice dictation pushes interim
   *  and final transcripts through this without owning a controlled
   *  binding. */
  setValue?: (value: string) => void;
  /** Attach already-resolved files through the composer's validated attach
   *  pipeline (size / type / count checks + upload + staging tray) — the
   *  same entry point the paperclip, paste and drag-drop use. Present only
   *  when the composer mounts the attach pipeline. A native shell (WKWebView /
   *  WebView2) that intercepts an OS file drop hands the bytes here so a
   *  native drop behaves exactly like an in-page one. */
  attachFiles?: (files: File[]) => void;
}

/**
 * `@djangocfg/widget-forms/composer-registry`
 *
 * Cross-tool bridge: the currently-active text composer's handle.
 *
 * Producer side (`@djangocfg/widget-chat` and TipTap hosts):
 *   register their composer's imperative handle via `attachComposer`.
 *
 * Consumer side (`@djangocfg/widget-forms/speech-recognition`):
 *   reads the active handle via `useActiveComposer`/`getActiveComposer`
 *   and pipes voice transcripts into it.
 *
 * Why this lives in its own subpath (not inside `chat`)
 * ----------------------------------------------------
 * `chat` and `speech-recognition` are sibling subpath exports. If the
 * registry lived inside `chat`, then `speech-recognition` would have
 * to reach into it via a cross-tool relative import — and under Vite
 * dev's dependency optimizer that file ends up loaded TWICE (once via
 * the `./chat` URL, once via the `./speech-recognition` relative-up
 * URL), giving the producer and the consumer two separate `let active`
 * slots. The active handle registered by chat would be invisible to
 * speech-recognition (and vice versa).
 *
 * Putting the registry in its own dedicated subpath (a single tool
 * that NEITHER chat nor speech-recognition cross-import — they both
 * import this one as their dependency) means Vite resolves it from a
 * single URL across the whole graph. One module instance, one shared
 * `active` slot.
 *
 * Semantics: one active composer per realm. The most recent
 * `registerComposer(handle)` wins; `registerComposer(null)` clears it.
 */

type Listener = (handle: ComposerHandle | null) => void;

let active: ComposerHandle | null = null;
const listeners = new Set<Listener>();

/** Set or replace the active composer handle. Pass `null` to clear. */
export function registerComposer(handle: ComposerHandle | null): void {
  active = handle;
  for (const fn of listeners) fn(active);
}

/**
 * Convenience for components: register on mount, unregister on
 * unmount. Returns a cleanup function suitable for `useEffect`.
 */
export function attachComposer(handle: ComposerHandle): () => void {
  registerComposer(handle);
  return () => {
    if (active === handle) registerComposer(null);
  };
}

/** Read the current active handle (no subscription). */
export function getActiveComposer(): ComposerHandle | null {
  return active;
}

// ── submit notifications ───────────────────────────────────────────────────
// A second tiny bus on the same shared module: the composer announces
// every REAL submit (guards passed, message is going out) so external
// tools can end their session — voice dictation stops recording the
// moment the user hits Send instead of talking into a sent message.

const submitListeners = new Set<() => void>();

/** Producer side — composers call this right before dispatching a submit. */
export function notifyComposerSubmit(): void {
  for (const fn of submitListeners) fn();
}

/** Consumer side — returns an unsubscribe fn. */
export function subscribeComposerSubmit(listener: () => void): () => void {
  submitListeners.add(listener);
  return () => {
    submitListeners.delete(listener);
  };
}

/** Subscribe to handle changes; returns an unsubscribe fn. */
export function subscribeComposer(listener: Listener): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

/**
 * React hook: re-renders the caller whenever the active composer
 * changes. Built on `useSyncExternalStore` so concurrent rendering,
 * SSR, and dev-mode strict-effects all behave correctly.
 */
export function useActiveComposer(): ComposerHandle | null {
  const subscribe = useCallback((onChange: () => void) => {
    return subscribeComposer(onChange);
  }, []);
  return useSyncExternalStore(subscribe, getActiveComposer, () => null);
}

// Composer control scale — shared by the chat's own action bar and by slot
// widgets rendered from this package. Lives beside the registry for the same
// reason the registry does: it is the seam BETWEEN the two, owned by neither.
export {
  ComposerSizeProvider,
  useResolvedComposerSize,
  type ComposerSize,
} from './size-context';
