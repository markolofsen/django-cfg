'use client';

import type { FlatRow, TreeNode } from '../../types';

/** Find the first row whose name starts with `prefix` (case-insensitive). */
export function findRowByPrefix<T>(
  rows: readonly FlatRow<T>[],
  getName: (node: TreeNode<T>) => string,
  prefix: string,
): FlatRow<T> | undefined {
  if (prefix.length === 0) return undefined;
  return rows.find((row) => getName(row.node).toLowerCase().startsWith(prefix));
}

/**
 * Should this key terminate type-ahead instead of extending the buffer?
 * Navigation, Enter, Tab, Escape — all reset; everything else continues.
 */
export function isResetKey(key: string): boolean {
  return (
    key === 'Escape' ||
    key === 'Enter' ||
    key === 'Tab' ||
    key.startsWith('Arrow') ||
    key === 'Home' ||
    key === 'End' ||
    key === 'PageUp' ||
    key === 'PageDown'
  );
}

/**
 * Skip keystrokes that originate inside a text field so type-ahead
 * doesn't yank focus while the user is filling in a form.
 */
export function isTypingTarget(target: EventTarget | null): boolean {
  const el = target as HTMLElement | null;
  if (!el) return false;
  const tag = el.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true;
  return el.isContentEditable === true;
}
