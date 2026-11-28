// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import { useMemo } from 'react';
import {
  computeStats,
  diffLines,
  lineNumberWidth,
  parseUnifiedPatch,
} from '../utils/computeDiff';
import type { DiffInput, DiffLine, DiffStats } from '../types';

interface UseDiffOptions {
  input: DiffInput;
  /** Context lines around each change-hunk. @default 3 */
  context?: number;
}

interface UseDiffResult {
  lines: DiffLine[];
  numWidth: number;
  stats: DiffStats;
}

/**
 * Memoize the diff computation so a re-render of the viewer (e.g. tab
 * switch, header copy click) doesn't re-run the LCS. The dependency
 * surface intentionally narrows to the two input strings / patch — the
 * `context` knob too, since a different window emits a different line
 * list.
 */
export function useDiff({ input, context = 3 }: UseDiffOptions): UseDiffResult {
  const isPatch = 'patch' in input && typeof input.patch === 'string';
  const oldCode = isPatch ? '' : input.oldCode;
  const newCode = isPatch ? '' : input.newCode;
  const patch = isPatch ? (input as { patch: string }).patch : '';

  return useMemo(() => {
    const lines = isPatch
      ? parseUnifiedPatch(patch)
      : diffLines(oldCode, newCode, context);
    return {
      lines,
      numWidth: lineNumberWidth(lines),
      stats: computeStats(lines),
    };
  }, [isPatch, patch, oldCode, newCode, context]);
}
