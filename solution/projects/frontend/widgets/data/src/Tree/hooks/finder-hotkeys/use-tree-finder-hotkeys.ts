'use client';

import { useCallback, useRef } from 'react';
import { useHotkey } from '@djangocfg/ui-core/hooks';

import { runBuiltinAction, type BuiltinActionContext } from '../../context/menu';
import type {
  TreeAdapter,
  TreeBuiltinAction,
  TreeItemId,
  TreeLabels,
  TreeNode,
} from '../../types';
import { buildBuiltinCtx } from './build-ctx';

export interface UseTreeFinderHotkeysOptions<T> {
  /** Off by default — Tree opt-ins via `enableFinderHotkeys`. */
  enabled: boolean;
  /** Adapter — used both for action availability and dispatch. */
  adapter?: TreeAdapter<T>;
  /** Labels (passed through into adapter action context for dialogs). */
  labels: TreeLabels;
  /** Live selection (set of ids). */
  selected: ReadonlySet<TreeItemId>;
  /** Live focused id (used as "target" for new-file/new-folder actions). */
  focused: TreeItemId | null;
  /** Id → node lookup. */
  getNodeById: (id: TreeItemId) => TreeNode<T> | undefined;
  /** Display name resolver. */
  getItemName: (node: TreeNode<T>) => string;
  /** Open inline rename on the row (P3). Falls back to a prompt otherwise. */
  startInlineRename?: (id: TreeItemId) => void;
  /** Clipboard bindings (P5). When undefined, ⌘C/X/V are no-ops. */
  clipboard?: BuiltinActionContext<T>['clipboard'];
  /** Whether typing is currently in inline-rename input — pauses bindings. */
  paused?: boolean;
}

export interface UseTreeFinderHotkeysReturn {
  /** Attach to the tree container ref so hotkeys only fire when it has focus. */
  ref: (instance: HTMLElement | null) => void;
}

/**
 * Wire the platform-aware Finder/Explorer shortcuts to the built-in
 * adapter actions. Bindings are scoped to the container ref via
 * `useHotkey`, so they don't leak to the rest of the page.
 *
 * Each shortcut is bound by an explicit `useHotkey` call (no `.map(useHotkey)`
 * loop, so the rules-of-hooks lint passes cleanly). The handler routes
 * through `runBuiltinAction`, which silently no-ops when the adapter
 * doesn't expose the matching method — so a Tree with `adapter = { remove }`
 * only effectively reacts to ⌘⌫ / Delete.
 */
export function useTreeFinderHotkeys<T>(
  opts: UseTreeFinderHotkeysOptions<T>,
): UseTreeFinderHotkeysReturn {
  const optsRef = useRef(opts);
  optsRef.current = opts;

  const run = useCallback(async (action: TreeBuiltinAction) => {
    const o = optsRef.current;
    if (o.paused) return;
    const ctx = buildBuiltinCtx({
      adapter: o.adapter,
      labels: o.labels,
      selected: o.selected,
      focused: o.focused,
      getNodeById: o.getNodeById,
      getItemName: o.getItemName,
      startInlineRename: o.startInlineRename,
      clipboard: o.clipboard,
    });
    if (!ctx) return;
    await runBuiltinAction(action, ctx);
  }, []);

  // One explicit binding per shortcut. Adding a new built-in action means
  // adding one more line here — the trade-off is verbose-but-static vs.
  // a fragile `.map(useHotkey)` loop.

  const refDelete = useHotkey(
    ['mod+backspace', 'delete'],
    () => void run('delete'),
    {
      enabled: opts.enabled,
      preventDefault: true,
      description: 'Delete selected items',
      scope: 'tree',
    },
  );

  const refRename = useHotkey('f2', () => void run('rename'), {
    enabled: opts.enabled,
    preventDefault: true,
    description: 'Rename selected item',
    scope: 'tree',
  });

  const refDuplicate = useHotkey('mod+d', () => void run('duplicate'), {
    enabled: opts.enabled,
    preventDefault: true,
    description: 'Duplicate selected items',
    scope: 'tree',
  });

  const refNewFolder = useHotkey('mod+shift+n', () => void run('new-folder'), {
    enabled: opts.enabled,
    preventDefault: true,
    description: 'New folder',
    scope: 'tree',
  });

  const refNewFile = useHotkey('mod+n', () => void run('new-file'), {
    enabled: opts.enabled,
    preventDefault: true,
    description: 'New file',
    scope: 'tree',
  });

  const refCut = useHotkey('mod+x', () => void run('cut'), {
    enabled: opts.enabled,
    preventDefault: true,
    description: 'Cut',
    scope: 'tree',
  });

  const refCopy = useHotkey('mod+c', () => void run('copy'), {
    enabled: opts.enabled,
    preventDefault: true,
    description: 'Copy',
    scope: 'tree',
  });

  const refPaste = useHotkey('mod+v', () => void run('paste'), {
    enabled: opts.enabled,
    preventDefault: true,
    description: 'Paste',
    scope: 'tree',
  });

  const ref = useCallback(
    (instance: HTMLElement | null) => {
      refDelete(instance);
      refRename(instance);
      refDuplicate(instance);
      refNewFolder(instance);
      refNewFile(instance);
      refCut(instance);
      refCopy(instance);
      refPaste(instance);
    },
    [
      refDelete,
      refRename,
      refDuplicate,
      refNewFolder,
      refNewFile,
      refCut,
      refCopy,
      refPaste,
    ],
  );

  return { ref };
}
