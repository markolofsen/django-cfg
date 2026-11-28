'use client';

import type { ClipboardState } from '../../data/clipboard';
import type { TreeItemId, TreeSelectionMode } from '../../types';

/**
 * The full reducer state for `<TreeProvider>`. Async children live
 * outside this object (see `async-children/` hook) since they're
 * managed via refs to avoid React re-renders on every fetch.
 */
export interface State {
  expanded: Set<TreeItemId>;
  selected: Set<TreeItemId>;
  /** Anchor for shift-range selection (Finder/Explorer). */
  anchor: TreeItemId | null;
  focused: TreeItemId | null;
  query: string;
  /** Id of the row currently in inline-rename mode (P3). */
  renaming: TreeItemId | null;
  /** Tree-local clipboard (cut / copy) — P5. */
  clipboard: ClipboardState;
  /** Bumped on every cache mutation so memos see a fresh dep. */
  cacheTick: number;
}

export type Action =
  | { type: 'expand'; id: TreeItemId }
  | { type: 'collapse'; id: TreeItemId }
  | { type: 'toggle'; id: TreeItemId }
  | { type: 'set-expanded'; ids: TreeItemId[] }
  | { type: 'select'; id: TreeItemId; mode: TreeSelectionMode }
  | { type: 'select-many'; ids: TreeItemId[] }
  | { type: 'clear-selection' }
  | {
      type: 'selection-replace';
      selected: TreeItemId[];
      anchor: TreeItemId | null;
      focused: TreeItemId | null;
    }
  | { type: 'set-anchor'; id: TreeItemId | null }
  | { type: 'focus'; id: TreeItemId | null }
  | { type: 'set-query'; q: string }
  | { type: 'start-rename'; id: TreeItemId }
  | { type: 'stop-rename' }
  | { type: 'clipboard-set'; payload: ClipboardState }
  | { type: 'cache-tick' };
