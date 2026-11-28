'use client';

import type { PersistedTreeState } from '../../data/persist';
import type { TreeItemId } from '../../types';
import type { State } from './types';

export interface CreateInitialStateInput {
  persisted: PersistedTreeState | null;
  initialExpandedIds?: TreeItemId[];
  initialSelectedIds?: TreeItemId[];
  persistSelection: boolean;
}

/**
 * Build the reducer's initial state from persistence + initial props.
 * Anchor is set to the first restored selection (if any) so a hard
 * reload doesn't break shift-extend.
 */
export function createInitialState(input: CreateInitialStateInput): State {
  const { persisted, initialExpandedIds, initialSelectedIds, persistSelection } =
    input;
  const initialSelected = new Set(
    (persistSelection ? persisted?.selectedItems : undefined) ??
      initialSelectedIds ??
      [],
  );
  const initialAnchor: TreeItemId | null =
    initialSelected.size > 0
      ? (initialSelected.values().next().value as TreeItemId)
      : null;
  return {
    expanded: new Set(persisted?.expandedItems ?? initialExpandedIds ?? []),
    selected: initialSelected,
    anchor: initialAnchor,
    focused: null,
    query: '',
    renaming: null,
    clipboard: null,
    cacheTick: 0,
  };
}
