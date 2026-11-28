import { describe, expect, it } from 'vitest';

import {
  computeRange,
  selectionFromClick,
  selectionFromMove,
  selectionSelectAll,
  selectionClear,
  type SelectionState,
} from '../data/selection';
import type { FlatRow } from '../types';

// =====================================================================
// Test fixtures
// =====================================================================

function row(id: string): FlatRow<unknown> {
  return {
    node: { id, data: undefined },
    level: 0,
    parentId: null,
    isFolder: false,
    isExpanded: false,
    isLoading: false,
    hasError: false,
    posInSet: 1,
    setSize: 1,
  };
}

const rows = ['a', 'b', 'c', 'd', 'e'].map(row);

const emptyState: SelectionState = {
  selected: new Set(),
  anchor: null,
  focused: null,
};

// =====================================================================
// computeRange
// =====================================================================

describe('computeRange', () => {
  it('returns ids between anchor and target (inclusive)', () => {
    expect(computeRange(rows, 'b', 'd')).toEqual(['b', 'c', 'd']);
  });

  it('works when target is before anchor', () => {
    expect(computeRange(rows, 'd', 'b')).toEqual(['b', 'c', 'd']);
  });

  it('returns a single id when from === to', () => {
    expect(computeRange(rows, 'c', 'c')).toEqual(['c']);
  });

  it('returns empty array when endpoint is missing', () => {
    expect(computeRange(rows, 'b', 'missing')).toEqual([]);
    expect(computeRange(rows, 'missing', 'b')).toEqual([]);
  });

  it('returns empty array when from or to is null', () => {
    expect(computeRange(rows, null, 'b')).toEqual([]);
    expect(computeRange(rows, 'b', null)).toEqual([]);
  });
});

// =====================================================================
// selectionFromClick
// =====================================================================

describe('selectionFromClick (single-select mode)', () => {
  it('collapses any modifier combo to one id when multi is false', () => {
    const next = selectionFromClick(
      { selected: new Set(['a', 'b']), anchor: 'a', focused: 'b' },
      rows,
      'c',
      { shift: true, meta: true },
      false,
    );
    expect([...next.selected]).toEqual(['c']);
    expect(next.anchor).toBe('c');
    expect(next.focused).toBe('c');
  });
});

describe('selectionFromClick (multi-select mode)', () => {
  it('plain click replaces selection and resets anchor', () => {
    const next = selectionFromClick(
      { selected: new Set(['a', 'b']), anchor: 'a', focused: 'b' },
      rows,
      'd',
      { shift: false, meta: false },
      true,
    );
    expect([...next.selected]).toEqual(['d']);
    expect(next.anchor).toBe('d');
    expect(next.focused).toBe('d');
  });

  it('meta-click toggles a single id and updates anchor', () => {
    const next = selectionFromClick(
      { selected: new Set(['a', 'b']), anchor: 'a', focused: 'b' },
      rows,
      'c',
      { shift: false, meta: true },
      true,
    );
    expect([...next.selected].sort()).toEqual(['a', 'b', 'c']);
    expect(next.anchor).toBe('c');
  });

  it('meta-click removes an already-selected id', () => {
    const next = selectionFromClick(
      { selected: new Set(['a', 'b']), anchor: 'a', focused: 'b' },
      rows,
      'b',
      { shift: false, meta: true },
      true,
    );
    expect([...next.selected]).toEqual(['a']);
    expect(next.anchor).toBe('b');
  });

  it('shift-click selects range from anchor to clicked row', () => {
    const next = selectionFromClick(
      { selected: new Set(['b']), anchor: 'b', focused: 'b' },
      rows,
      'd',
      { shift: true, meta: false },
      true,
    );
    expect([...next.selected]).toEqual(['b', 'c', 'd']);
    expect(next.anchor).toBe('b'); // anchor stays put
    expect(next.focused).toBe('d');
  });

  it('shift-click without anchor falls back to focused', () => {
    const next = selectionFromClick(
      { selected: new Set(['c']), anchor: null, focused: 'c' },
      rows,
      'e',
      { shift: true, meta: false },
      true,
    );
    expect([...next.selected]).toEqual(['c', 'd', 'e']);
  });

  it('shift+meta unions the range with existing selection', () => {
    const next = selectionFromClick(
      { selected: new Set(['a']), anchor: 'b', focused: 'b' },
      rows,
      'd',
      { shift: true, meta: true },
      true,
    );
    expect([...next.selected].sort()).toEqual(['a', 'b', 'c', 'd']);
    expect(next.anchor).toBe('b');
  });
});

// =====================================================================
// selectionFromMove
// =====================================================================

describe('selectionFromMove', () => {
  it('non-extend move collapses to single id', () => {
    const next = selectionFromMove(
      { selected: new Set(['a', 'b']), anchor: 'a', focused: 'b' },
      rows,
      'c',
      false,
      true,
    );
    expect([...next.selected]).toEqual(['c']);
    expect(next.anchor).toBe('c');
  });

  it('extend move with anchor recomputes range', () => {
    const next = selectionFromMove(
      { selected: new Set(['b']), anchor: 'b', focused: 'b' },
      rows,
      'd',
      true,
      true,
    );
    expect([...next.selected]).toEqual(['b', 'c', 'd']);
    expect(next.anchor).toBe('b');
    expect(next.focused).toBe('d');
  });

  it('extend without multi-select treats it as a plain move', () => {
    const next = selectionFromMove(emptyState, rows, 'c', true, false);
    expect([...next.selected]).toEqual(['c']);
  });
});

// =====================================================================
// selectionSelectAll + selectionClear
// =====================================================================

describe('selectionSelectAll', () => {
  it('selects every visible id and anchors the first row', () => {
    const next = selectionSelectAll(rows, 'c');
    expect([...next.selected]).toEqual(['a', 'b', 'c', 'd', 'e']);
    expect(next.anchor).toBe('a');
    expect(next.focused).toBe('c');
  });

  it('returns empty state for an empty row list', () => {
    const next = selectionSelectAll([], null);
    expect(next.selected.size).toBe(0);
    expect(next.anchor).toBeNull();
  });
});

describe('selectionClear', () => {
  it('drops selection and anchor but keeps focused', () => {
    const next = selectionClear({
      selected: new Set(['a', 'b']),
      anchor: 'a',
      focused: 'b',
    });
    expect(next.selected.size).toBe(0);
    expect(next.anchor).toBeNull();
    expect(next.focused).toBe('b');
  });
});
