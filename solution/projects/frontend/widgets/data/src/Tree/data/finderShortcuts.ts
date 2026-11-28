'use client';

import type { TreeBuiltinAction } from '../types';

// =====================================================================
// Finder / Explorer keyboard shortcuts.
//
// Each entry maps a built-in action to a list of `react-hotkeys-hook`
// combos. `mod` resolves to ⌘ on macOS and Ctrl on Win/Linux automatically,
// so a single declaration works cross-platform.
//
// Tree only binds shortcuts whose corresponding adapter method is
// defined. So `delete` only fires if `adapter.remove` exists — same
// gating used for context-menu items, no duplicated source of truth.
// =====================================================================

export interface FinderShortcut {
  /** Built-in action id this shortcut runs. */
  action: TreeBuiltinAction;
  /** `react-hotkeys-hook` key combos. */
  keys: string[];
  /** Cheat-sheet description (registered via `useHotkey`). */
  description: string;
}

export const FINDER_SHORTCUTS: FinderShortcut[] = [
  {
    action: 'delete',
    keys: ['mod+backspace', 'delete'],
    description: 'Delete selected items',
  },
  {
    action: 'rename',
    keys: ['f2'],
    description: 'Rename selected item',
  },
  {
    action: 'duplicate',
    keys: ['mod+d'],
    description: 'Duplicate selected items',
  },
  {
    action: 'new-folder',
    keys: ['mod+shift+n'],
    description: 'New folder',
  },
  {
    action: 'new-file',
    keys: ['mod+n'],
    description: 'New file',
  },
  {
    action: 'cut',
    keys: ['mod+x'],
    description: 'Cut',
  },
  {
    action: 'copy',
    keys: ['mod+c'],
    description: 'Copy',
  },
  {
    action: 'paste',
    keys: ['mod+v'],
    description: 'Paste',
  },
];
