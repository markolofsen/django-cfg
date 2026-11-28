import { describe, expect, it } from 'vitest';

import { computeStats, diffLines, lineNumberWidth, parseUnifiedPatch } from './computeDiff';

/**
 * The diff viewer shows people what changed before they approve it. A wrong
 * line number or a swapped +/- tag is not a cosmetic bug — it is a reviewer
 * agreeing to a change they were shown incorrectly.
 *
 * The LCS walk-back is the part with no safety net: it reconstructs the
 * sequence in reverse and assigns both line-number columns as it goes, so an
 * off-by-one there produces output that still looks plausible.
 */

describe('diffLines — identical input', () => {
  it('emits no added or removed lines', () => {
    const out = diffLines('a\nb\nc', 'a\nb\nc');
    expect(out.every((l) => l.type === 'context')).toBe(true);
  });

  it('drops all context when nothing changed, because nothing is within the window', () => {
    // No change anchors the context window, so every line is unkept. The
    // viewer showing an empty body for an unchanged file is the contract.
    expect(diffLines('a\nb\nc\nd\ne\nf\ng\nh', 'a\nb\nc\nd\ne\nf\ng\nh')).toEqual([]);
  });

  it('keeps every line when context is Infinity', () => {
    const out = diffLines('a\nb\nc', 'a\nb\nc', Infinity);
    expect(out).toHaveLength(3);
    expect(out.map((l) => l.content)).toEqual(['a', 'b', 'c']);
    expect(out.map((l) => l.oldNumber)).toEqual([1, 2, 3]);
    expect(out.map((l) => l.newNumber)).toEqual([1, 2, 3]);
  });
});

describe('diffLines — pure insertion', () => {
  it('tags only the new lines as added and leaves old numbering intact', () => {
    const out = diffLines('a\nb', 'a\nX\nb', Infinity);
    expect(out.map((l) => [l.type, l.content, l.oldNumber, l.newNumber])).toEqual([
      ['context', 'a', 1, 1],
      ['added', 'X', null, 2],
      ['context', 'b', 2, 3],
    ]);
  });

  it('handles an empty old side as an all-added file', () => {
    // `''.split('\n')` is `['']`, so the empty side contributes one empty line
    // which shows as a removal. Every line of the new side must still be added.
    const out = diffLines('', 'a\nb', Infinity);
    expect(out.filter((l) => l.type === 'added').map((l) => l.content)).toEqual(['a', 'b']);
    expect(out.filter((l) => l.type === 'removed').map((l) => l.content)).toEqual(['']);
  });
});

describe('diffLines — pure deletion', () => {
  it('tags only the dropped lines as removed and leaves new numbering intact', () => {
    const out = diffLines('a\nX\nb', 'a\nb', Infinity);
    expect(out.map((l) => [l.type, l.content, l.oldNumber, l.newNumber])).toEqual([
      ['context', 'a', 1, 1],
      ['removed', 'X', 2, null],
      ['context', 'b', 3, 2],
    ]);
  });

  it('handles an empty new side as an all-removed file', () => {
    const out = diffLines('a\nb', '', Infinity);
    expect(out.filter((l) => l.type === 'removed').map((l) => l.content)).toEqual(['a', 'b']);
    expect(out.filter((l) => l.type === 'added').map((l) => l.content)).toEqual(['']);
  });
});

describe('diffLines — a change in the middle', () => {
  const out = diffLines('a\nb\nc', 'a\nB\nc', Infinity);

  it('renders the change as a removal followed by an addition', () => {
    expect(out.map((l) => l.type)).toEqual(['context', 'removed', 'added', 'context']);
  });

  it('numbers both sides so the columns still line up after the change', () => {
    expect(out.map((l) => [l.content, l.oldNumber, l.newNumber])).toEqual([
      ['a', 1, 1],
      ['b', 2, null],
      ['B', null, 2],
      ['c', 3, 3],
    ]);
  });

  it('advances each side\'s numbering independently across an uneven change', () => {
    const uneven = diffLines('a\nb\nc\nd', 'a\nX\nY\nZ\nd', Infinity);
    const last = uneven[uneven.length - 1];
    expect(last?.content).toBe('d');
    expect(last?.oldNumber).toBe(4);
    expect(last?.newNumber).toBe(5);
  });
});

describe('diffLines — the context window', () => {
  const oldCode = Array.from({ length: 20 }, (_, i) => `line${i + 1}`).join('\n');
  const newCode = oldCode.replace('line10', 'CHANGED');

  it('keeps exactly `context` unchanged lines on each side of the change', () => {
    const out = diffLines(oldCode, newCode, 2);
    // 2 removed/added rows sit adjacent, so the window spans the union of
    // both anchors: lines 8,9 before and 11,12 after.
    expect(out.map((l) => l.content)).toEqual([
      'line8', 'line9', 'line10', 'CHANGED', 'line11', 'line12',
    ]);
  });

  it('drops distant context entirely rather than emitting a hunk separator', () => {
    const out = diffLines(oldCode, newCode, 1);
    expect(out.some((l) => l.content.startsWith('@@'))).toBe(false);
    expect(out.map((l) => l.content)).toEqual(['line9', 'line10', 'CHANGED', 'line11']);
  });

  it('emits nothing but the change itself at context 0', () => {
    const out = diffLines(oldCode, newCode, 0);
    expect(out.map((l) => [l.type, l.content])).toEqual([
      ['removed', 'line10'],
      ['added', 'CHANGED'],
    ]);
  });
});

describe('diffLines — degenerate inputs', () => {
  it('reports no change for two empty strings', () => {
    expect(diffLines('', '')).toEqual([]);
  });

  it('preserves blank lines as content, not as separators', () => {
    const out = diffLines('a\n\nb', 'a\n\nb', Infinity);
    expect(out.map((l) => l.content)).toEqual(['a', '', 'b']);
  });

  it('treats a whole-file rewrite as removals then additions', () => {
    const out = diffLines('a\nb', 'x\ny', Infinity);
    expect(out.filter((l) => l.type === 'context')).toEqual([]);
    expect(out.filter((l) => l.type === 'removed').map((l) => l.content)).toEqual(['a', 'b']);
    expect(out.filter((l) => l.type === 'added').map((l) => l.content)).toEqual(['x', 'y']);
  });
});

describe('parseUnifiedPatch', () => {
  it('numbers lines from the hunk header, not from the top of the patch', () => {
    const patch = [
      '--- a/file.ts',
      '+++ b/file.ts',
      '@@ -10,3 +10,4 @@',
      ' keep',
      '-gone',
      '+new1',
      '+new2',
      ' tail',
    ].join('\n');
    expect(parseUnifiedPatch(patch).map((l) => [l.type, l.content, l.oldNumber, l.newNumber])).toEqual([
      ['context', 'keep', 10, 10],
      ['removed', 'gone', 11, null],
      ['added', 'new1', null, 11],
      ['added', 'new2', null, 12],
      ['context', 'tail', 12, 13],
    ]);
  });

  it('ignores everything before the first hunk header', () => {
    expect(parseUnifiedPatch('diff --git a/x b/x\nindex 111..222\nnoise')).toEqual([]);
  });

  it('skips the "\\ No newline at end of file" marker', () => {
    const out = parseUnifiedPatch('@@ -1 +1 @@\n-a\n\\ No newline at end of file\n+b');
    expect(out.map((l) => l.type)).toEqual(['removed', 'added']);
  });

  it('accepts a single-line hunk header with no counts', () => {
    const out = parseUnifiedPatch('@@ -7 +9 @@\n ctx');
    expect(out[0]?.oldNumber).toBe(7);
    expect(out[0]?.newNumber).toBe(9);
  });

  it('restarts numbering at each subsequent hunk', () => {
    const out = parseUnifiedPatch('@@ -1,1 +1,1 @@\n a\n@@ -50,1 +60,1 @@\n b');
    expect(out.map((l) => [l.content, l.oldNumber, l.newNumber])).toEqual([
      ['a', 1, 1],
      ['b', 50, 60],
    ]);
  });
});

describe('lineNumberWidth', () => {
  it('never goes below 2, so the gutter does not jitter on short files', () => {
    expect(lineNumberWidth([])).toBe(2);
    expect(lineNumberWidth([{ type: 'context', content: 'a', oldNumber: 1, newNumber: 1 }])).toBe(2);
  });

  it('widens to the largest number on either side', () => {
    expect(lineNumberWidth([
      { type: 'context', content: 'a', oldNumber: 9, newNumber: 1234 },
    ])).toBe(4);
  });

  it('ignores the null column of an added or removed line', () => {
    expect(lineNumberWidth([
      { type: 'added', content: 'a', oldNumber: null, newNumber: 100 },
      { type: 'removed', content: 'b', oldNumber: 7, newNumber: null },
    ])).toBe(3);
  });
});

describe('computeStats', () => {
  it('counts added and removed and ignores context', () => {
    expect(computeStats([
      { type: 'added', content: '', oldNumber: null, newNumber: 1 },
      { type: 'added', content: '', oldNumber: null, newNumber: 2 },
      { type: 'removed', content: '', oldNumber: 1, newNumber: null },
      { type: 'context', content: '', oldNumber: 2, newNumber: 3 },
    ])).toEqual({ added: 2, removed: 1 });
  });

  it('is zero for an empty diff', () => {
    expect(computeStats([])).toEqual({ added: 0, removed: 0 });
  });
});
