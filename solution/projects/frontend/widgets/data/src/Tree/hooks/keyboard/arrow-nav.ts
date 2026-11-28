'use client';

import type { FlatRow, TreeItemId } from '../../types';

/** Pick the id one row below the current focused row (clamped at the end). */
export function nextRowId<T>(rows: readonly FlatRow<T>[], idx: number): TreeItemId | null {
  if (rows.length === 0) return null;
  const next = rows[Math.min(idx + 1, rows.length - 1)] ?? rows[0];
  return next ? next.node.id : null;
}

/** Pick the id one row above the current focused row (clamped at the start). */
export function prevRowId<T>(rows: readonly FlatRow<T>[], idx: number): TreeItemId | null {
  if (rows.length === 0) return null;
  const prev = rows[Math.max(idx - 1, 0)] ?? rows[0];
  return prev ? prev.node.id : null;
}

/** First / last visible row id, or null if the list is empty. */
export function edgeRowId<T>(
  rows: readonly FlatRow<T>[],
  edge: 'first' | 'last',
): TreeItemId | null {
  const row = edge === 'first' ? rows[0] : rows[rows.length - 1];
  return row ? row.node.id : null;
}
