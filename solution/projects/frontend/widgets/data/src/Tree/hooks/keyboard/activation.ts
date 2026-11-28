'use client';

import type { FlatRow } from '../../types';

/**
 * Enter / Space on the current row:
 *   - folder: toggle (collapse if expanded, else expand)
 *   - leaf:   activate
 *
 * Always selects (single-select semantics for keyboard input).
 */
export type ActivateOutcome =
  | { kind: 'toggle-folder'; id: string; willExpand: boolean }
  | { kind: 'activate-leaf'; id: string }
  | { kind: 'noop' };

export function resolveActivate<T>(current: FlatRow<T> | null): ActivateOutcome {
  if (!current) return { kind: 'noop' };
  if (current.isFolder) {
    return {
      kind: 'toggle-folder',
      id: current.node.id,
      willExpand: !current.isExpanded,
    };
  }
  return { kind: 'activate-leaf', id: current.node.id };
}
