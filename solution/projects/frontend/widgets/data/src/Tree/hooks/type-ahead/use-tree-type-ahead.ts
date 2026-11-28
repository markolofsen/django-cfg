'use client';

import { useEffect, useRef } from 'react';

import type { FlatRow, TreeNode } from '../../types';
import { findRowByPrefix, isResetKey, isTypingTarget } from './match-prefix';

const FLUSH_MS = 600;

export interface UseTreeTypeAheadOptions<T> {
  /** Visible flat rows in render order. */
  rows: FlatRow<T>[];
  /** How to read the displayed name of a node (matched case-insensitively). */
  getItemName: (node: TreeNode<T>) => string;
  /** Element receiving keydown events. */
  containerRef: React.RefObject<HTMLElement | null>;
  /** Called with the matched node id so the consumer can focus / scroll. */
  onMatch: (id: string) => void;
  /** Disable without removing the call site. */
  enabled?: boolean;
}

/**
 * Type-ahead jump (Finder / VSCode style).
 *
 * Builds a rolling buffer of printable keys (within ~600 ms of each other)
 * and notifies the consumer of the first row whose name starts with that
 * prefix. Resets on Esc / Enter / navigation keys / timeout.
 */
export function useTreeTypeAhead<T>({
  rows,
  getItemName,
  containerRef,
  onMatch,
  enabled = true,
}: UseTreeTypeAheadOptions<T>) {
  const bufferRef = useRef('');
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const rowsRef = useRef(rows);
  const getNameRef = useRef(getItemName);
  const onMatchRef = useRef(onMatch);
  rowsRef.current = rows;
  getNameRef.current = getItemName;
  onMatchRef.current = onMatch;

  useEffect(() => {
    if (!enabled) return;
    const target = containerRef.current;
    if (!target) return;

    const reset = () => {
      bufferRef.current = '';
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };

    const handler = (e: KeyboardEvent) => {
      if (isTypingTarget(e.target)) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (isResetKey(e.key)) {
        reset();
        return;
      }
      if (e.key.length !== 1) return;

      bufferRef.current += e.key.toLowerCase();
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(reset, FLUSH_MS);

      const hit = findRowByPrefix(
        rowsRef.current,
        getNameRef.current,
        bufferRef.current,
      );
      if (hit) {
        e.preventDefault();
        onMatchRef.current(hit.node.id);
      }
    };

    target.addEventListener('keydown', handler);
    return () => {
      target.removeEventListener('keydown', handler);
      reset();
    };
  }, [containerRef, enabled]);
}
