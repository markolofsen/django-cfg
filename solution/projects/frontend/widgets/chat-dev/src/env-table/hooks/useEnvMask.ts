// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import type { EnvVariable } from '../types';

const COPY_FEEDBACK_MS = 1500;

/**
 * Mask the value for display. Reveals the first 4 chars only when the value
 * is long enough — the raw `value` never leaks to the DOM in masked state.
 */
export function maskValue(value: string): string {
  if (value.length <= 4) return '••••••••';
  return value.slice(0, 4) + '••••••••';
}

export interface UseEnvMaskOptions {
  variables: EnvVariable[];
  defaultRevealed?: boolean;
}

export interface UseEnvMaskReturn {
  /** Set of indices currently revealed. */
  revealed: Set<number>;
  /** Whether every row is revealed. */
  allRevealed: boolean;
  /** Toggle a single row by index. */
  toggleIndex: (index: number) => void;
  /** Reveal-all / hide-all toggle. */
  toggleAll: () => void;
  /** Last-copied row index (or `'all'`) — null when feedback expired. */
  copiedTarget: number | 'all' | null;
  /** Copy a single value to clipboard, marking the row as copied. */
  copyValue: (index: number, value: string) => void;
  /** Copy every variable as a `.env`-style block. */
  copyAllAsEnv: () => void;
}

/**
 * Mask / reveal / copy state for {@link EnvTable}. The hook owns per-row
 * reveal state and short-lived "copied!" feedback flags.
 */
export function useEnvMask({
  variables,
  defaultRevealed = false,
}: UseEnvMaskOptions): UseEnvMaskReturn {
  const [revealed, setRevealed] = React.useState<Set<number>>(() =>
    defaultRevealed ? new Set(variables.map((_, i) => i)) : new Set(),
  );
  const [copiedTarget, setCopiedTarget] = React.useState<number | 'all' | null>(
    null,
  );
  const timerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  React.useEffect(
    () => () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    },
    [],
  );

  const flagCopied = React.useCallback((target: number | 'all') => {
    setCopiedTarget(target);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setCopiedTarget(null), COPY_FEEDBACK_MS);
  }, []);

  const allRevealed =
    variables.length > 0 && revealed.size === variables.length;

  const toggleIndex = React.useCallback((index: number) => {
    setRevealed((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }, []);

  const toggleAll = React.useCallback(() => {
    setRevealed((prev) =>
      prev.size === variables.length
        ? new Set()
        : new Set(variables.map((_, i) => i)),
    );
  }, [variables]);

  const copyValue = React.useCallback(
    (index: number, value: string) => {
      void navigator.clipboard
        .writeText(value)
        .then(() => flagCopied(index))
        .catch(() => {
          /* clipboard rejection — swallow, no feedback */
        });
    },
    [flagCopied],
  );

  const copyAllAsEnv = React.useCallback(() => {
    const text = variables.map((v) => `${v.key}=${v.value}`).join('\n');
    void navigator.clipboard
      .writeText(text)
      .then(() => flagCopied('all'))
      .catch(() => {
        /* swallow */
      });
  }, [variables, flagCopied]);

  return {
    revealed,
    allRevealed,
    toggleIndex,
    toggleAll,
    copiedTarget,
    copyValue,
    copyAllAsEnv,
  };
}
