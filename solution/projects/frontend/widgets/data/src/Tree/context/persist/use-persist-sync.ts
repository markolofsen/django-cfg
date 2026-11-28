'use client';

import { useEffect, useRef } from 'react';

import { saveTreeState } from '../../data/persist';
import type { TreeItemId } from '../../types';

export interface UsePersistSyncOptions {
  expanded: ReadonlySet<TreeItemId>;
  selected: ReadonlySet<TreeItemId>;
  persistKey?: string;
  persistSelection: boolean;
  onSelectionChange?: (ids: TreeItemId[]) => void;
  onExpansionChange?: (ids: TreeItemId[]) => void;
}

/**
 * Persist `expanded` / `selected` into `localStorage` under `persistKey`,
 * and forward changes through the consumer's notify callbacks. We
 * compare by content (not identity) because the reducer recreates
 * `Set`s on every change — without diffing we'd fire `onSelectionChange`
 * on every render.
 */
export function usePersistSync({
  expanded,
  selected,
  persistKey,
  persistSelection,
  onSelectionChange,
  onExpansionChange,
}: UsePersistSyncOptions): void {
  // Stable refs so we don't re-bind effects every render.
  const onSelectionChangeRef = useRef(onSelectionChange);
  const onExpansionChangeRef = useRef(onExpansionChange);
  onSelectionChangeRef.current = onSelectionChange;
  onExpansionChangeRef.current = onExpansionChange;

  const lastSelectedArrRef = useRef<TreeItemId[]>([...selected]);
  const lastExpandedArrRef = useRef<TreeItemId[]>([...expanded]);

  useEffect(() => {
    const arr = [...expanded];
    if (!setEqualsArr(expanded, lastExpandedArrRef.current)) {
      lastExpandedArrRef.current = arr;
      onExpansionChangeRef.current?.(arr);
      if (persistKey) {
        saveTreeState(persistKey, {
          expandedItems: arr,
          selectedItems: persistSelection ? [...selected] : [],
        });
      }
    }
  }, [expanded, persistKey, persistSelection, selected]);

  useEffect(() => {
    const arr = [...selected];
    if (!setEqualsArr(selected, lastSelectedArrRef.current)) {
      lastSelectedArrRef.current = arr;
      onSelectionChangeRef.current?.(arr);
      if (persistKey && persistSelection) {
        saveTreeState(persistKey, {
          expandedItems: [...expanded],
          selectedItems: arr,
        });
      }
    }
  }, [selected, persistKey, persistSelection, expanded]);
}

function setEqualsArr(set: ReadonlySet<string>, arr: readonly string[]): boolean {
  if (set.size !== arr.length) return false;
  for (const id of arr) if (!set.has(id)) return false;
  return true;
}
