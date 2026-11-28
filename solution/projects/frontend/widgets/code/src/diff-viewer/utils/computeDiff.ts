// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Line-level diff via Longest Common Subsequence. The jalcoui original
// uses the `diff` npm package (Myers diff + unified patches). We don't
// pull that dependency: a 60-line LCS in TS handles up to ~5k lines
// fast enough for the viewer's use case (small/medium code reviews) and
// keeps the bundle lean. For pre-computed patches the caller can pass
// `patch` and we parse the unified-diff text directly — no algorithm
// runs at all.

import type { DiffLine } from '../types';

/**
 * Compute line-level diff between two strings. Returns a flat sequence
 * of `DiffLine`s in display order. `context` controls how many unchanged
 * lines are emitted around each change-hunk; pass `Infinity` to keep the
 * full file.
 */
export function diffLines(
  oldCode: string,
  newCode: string,
  context = 3,
): DiffLine[] {
  const oldLines = oldCode.split('\n');
  const newLines = newCode.split('\n');

  // Build LCS table (rows = oldLines + 1, cols = newLines + 1).
  // For each cell, store the length of the longest common subsequence
  // of `oldLines[0..i]` and `newLines[0..j]`.
  const m = oldLines.length;
  const n = newLines.length;
  // Use a single flat Int32Array for cache friendliness.
  const lcs = new Int32Array((m + 1) * (n + 1));
  const cols = n + 1;
  // Every `lcs` index below is derived from the loop bounds and is therefore
  // in range; `at()` would cost a bounds re-check per cell in the hot loop, so
  // read through a helper that keeps the `number` type without changing the
  // arithmetic.
  const cell = (index: number): number => lcs[index] ?? 0;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const idx = i * cols + j;
      if (oldLines[i - 1] === newLines[j - 1]) {
        lcs[idx] = cell((i - 1) * cols + (j - 1)) + 1;
      } else {
        const up = cell((i - 1) * cols + j);
        const left = cell(i * cols + (j - 1));
        lcs[idx] = up >= left ? up : left;
      }
    }
  }

  // Walk back from (m, n) to (0, 0) emitting tagged lines.
  type Tagged = { type: DiffLine['type']; oldNum: number | null; newNum: number | null; content: string };
  const tagged: Tagged[] = [];
  let i = m;
  let j = n;
  while (i > 0 || j > 0) {
    // `i`/`j` are > 0 in each branch that indexes, so the reads are in range;
    // the `?? ''` only satisfies noUncheckedIndexedAccess.
    if (i > 0 && j > 0 && oldLines[i - 1] === newLines[j - 1]) {
      tagged.push({ type: 'context', oldNum: i, newNum: j, content: oldLines[i - 1] ?? '' });
      i--;
      j--;
    } else if (j > 0 && (i === 0 || cell(i * cols + (j - 1)) >= cell((i - 1) * cols + j))) {
      tagged.push({ type: 'added', oldNum: null, newNum: j, content: newLines[j - 1] ?? '' });
      j--;
    } else if (i > 0) {
      tagged.push({ type: 'removed', oldNum: i, newNum: null, content: oldLines[i - 1] ?? '' });
      i--;
    }
  }
  tagged.reverse();

  // Apply context window — drop runs of `context`-only lines that are
  // farther than `context` from any change. `Infinity` keeps every line.
  if (!Number.isFinite(context)) {
    return tagged.map((t) => ({
      type: t.type,
      content: t.content,
      oldNumber: t.oldNum,
      newNumber: t.newNum,
    }));
  }

  // Mark indices that are within `context` of a change.
  const keep = new Array<boolean>(tagged.length).fill(false);
  for (let k = 0; k < tagged.length; k++) {
    const t = tagged[k];
    if (t === undefined) continue;
    if (t.type !== 'context') {
      const from = Math.max(0, k - context);
      const to = Math.min(tagged.length - 1, k + context);
      for (let s = from; s <= to; s++) keep[s] = true;
    }
  }

  // Drop unkept context lines. We don't render hunk separators (`@@`) —
  // the viewer is meant for compact diffs, not full-file patches.
  const out: DiffLine[] = [];
  for (let k = 0; k < tagged.length; k++) {
    if (!keep[k]) continue;
    const t = tagged[k];
    if (t === undefined) continue;
    out.push({
      type: t.type,
      content: t.content,
      oldNumber: t.oldNum,
      newNumber: t.newNum,
    });
  }
  return out;
}

/**
 * Parse a unified diff patch (`@@ -a,b +c,d @@` hunks) into the same
 * `DiffLine[]` shape `diffLines()` produces. Only the line tags and
 * numbers from the hunk headers are honored — file headers
 * (`--- a/file`, `+++ b/file`) are skipped.
 */
export function parseUnifiedPatch(patch: string): DiffLine[] {
  const lines: DiffLine[] = [];
  const HUNK = /^@@\s+-(\d+)(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@/;
  let oldNum = 0;
  let newNum = 0;
  let inHunk = false;

  for (const raw of patch.split('\n')) {
    const hunk = HUNK.exec(raw);
    if (hunk) {
      // Both groups are non-optional in HUNK, so a match always fills them.
      oldNum = parseInt(hunk[1] ?? '0', 10);
      newNum = parseInt(hunk[2] ?? '0', 10);
      inHunk = true;
      continue;
    }
    if (!inHunk) continue;
    if (raw.startsWith('--- ') || raw.startsWith('+++ ') || raw.startsWith('\\')) continue;

    if (raw.startsWith('+')) {
      lines.push({ type: 'added', content: raw.slice(1), oldNumber: null, newNumber: newNum++ });
    } else if (raw.startsWith('-')) {
      lines.push({ type: 'removed', content: raw.slice(1), oldNumber: oldNum++, newNumber: null });
    } else {
      const content = raw.startsWith(' ') ? raw.slice(1) : raw;
      lines.push({ type: 'context', content, oldNumber: oldNum++, newNumber: newNum++ });
    }
  }
  return lines;
}

/** Widest gutter required for the line numbers, in characters. */
export function lineNumberWidth(lines: DiffLine[]): number {
  let max = 0;
  for (const line of lines) {
    if (line.oldNumber && line.oldNumber > max) max = line.oldNumber;
    if (line.newNumber && line.newNumber > max) max = line.newNumber;
  }
  return Math.max(String(max).length, 2);
}

/** Count `+` and `-` lines for the header stat pill. */
export function computeStats(lines: DiffLine[]): { added: number; removed: number } {
  let added = 0;
  let removed = 0;
  for (const line of lines) {
    if (line.type === 'added') added++;
    else if (line.type === 'removed') removed++;
  }
  return { added, removed };
}
