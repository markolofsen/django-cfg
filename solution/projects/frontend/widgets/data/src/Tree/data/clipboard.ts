'use client';

import type { TreeItemId } from '../types';

// =====================================================================
// Tree-local clipboard.
//
// Why not the system clipboard? Because we need a visual "cut" state
// (Finder/Explorer dim cut items) and a single source of truth across
// Tree's own keyboard / menu / DnD entry points. The system clipboard
// can't carry that semantics in a way that survives focus changes.
//
// Clipboard owns *ids*, not full nodes — Tree resolves them through
// `getNodeById` at paste time. This keeps the model immutable to the
// underlying data refreshing under us (async load, refresh, etc.).
// =====================================================================

export type ClipboardKind = 'cut' | 'copy';

export interface ClipboardEntry {
  kind: ClipboardKind;
  ids: TreeItemId[];
}

export type ClipboardState = ClipboardEntry | null;

/**
 * Was this id put on the clipboard with `kind: 'cut'`? Used by `TreeRow`
 * to render dimmed (`opacity-60`) rows the way Finder does.
 */
export function isCutId(state: ClipboardState, id: TreeItemId): boolean {
  return state?.kind === 'cut' && state.ids.includes(id);
}
