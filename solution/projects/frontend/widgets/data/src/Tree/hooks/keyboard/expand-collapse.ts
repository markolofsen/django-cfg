'use client';

import type { FlatRow } from '../../types';

/**
 * What should `→` do on the current row?
 *
 *   - collapsed folder → expand it
 *   - expanded folder  → jump to first visible child
 *   - leaf             → no-op
 */
export type RightArrowOutcome =
  | { kind: 'expand'; id: string }
  | { kind: 'focus'; id: string }
  | { kind: 'noop' };

export function resolveRightArrow<T>(
  current: FlatRow<T> | null,
  rows: readonly FlatRow<T>[],
  idx: number,
): RightArrowOutcome {
  if (!current) return { kind: 'noop' };
  if (current.isFolder && !current.isExpanded) {
    return { kind: 'expand', id: current.node.id };
  }
  if (current.isFolder && current.isExpanded) {
    const next = rows[idx + 1];
    return next ? { kind: 'focus', id: next.node.id } : { kind: 'noop' };
  }
  return { kind: 'noop' };
}

/**
 * What should `←` do on the current row?
 *
 *   - expanded folder           → collapse it
 *   - leaf / collapsed w/ parent → focus parent
 *   - root leaf                  → no-op
 */
export type LeftArrowOutcome =
  | { kind: 'collapse'; id: string }
  | { kind: 'focus'; id: string }
  | { kind: 'noop' };

export function resolveLeftArrow<T>(current: FlatRow<T> | null): LeftArrowOutcome {
  if (!current) return { kind: 'noop' };
  if (current.isFolder && current.isExpanded) {
    return { kind: 'collapse', id: current.node.id };
  }
  if (current.parentId) {
    return { kind: 'focus', id: current.parentId };
  }
  return { kind: 'noop' };
}
