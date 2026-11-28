import { describe, expect, it } from 'vitest';

import { edgeRowId, nextRowId, prevRowId } from '../hooks/keyboard/arrow-nav';
import { resolveActivate } from '../hooks/keyboard/activation';
import {
  resolveLeftArrow,
  resolveRightArrow,
} from '../hooks/keyboard/expand-collapse';
import type { FlatRow } from '../types';

function row(
  id: string,
  overrides: Partial<FlatRow<unknown>> = {},
): FlatRow<unknown> {
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
    ...overrides,
  };
}

const rows = ['a', 'b', 'c'].map((id) => row(id));

// ----------------------------------------------------------------------
// arrow-nav
// ----------------------------------------------------------------------

describe('nextRowId / prevRowId', () => {
  it('moves one row forward / back', () => {
    expect(nextRowId(rows, 0)).toBe('b');
    expect(prevRowId(rows, 2)).toBe('b');
  });

  it('clamps at edges', () => {
    expect(nextRowId(rows, 2)).toBe('c'); // last → last
    expect(prevRowId(rows, 0)).toBe('a'); // first → first
  });

  it('returns null on empty list', () => {
    expect(nextRowId([], 0)).toBeNull();
    expect(prevRowId([], 0)).toBeNull();
  });
});

describe('edgeRowId', () => {
  it('picks first / last row', () => {
    expect(edgeRowId(rows, 'first')).toBe('a');
    expect(edgeRowId(rows, 'last')).toBe('c');
  });

  it('returns null on empty list', () => {
    expect(edgeRowId([], 'first')).toBeNull();
  });
});

// ----------------------------------------------------------------------
// expand-collapse
// ----------------------------------------------------------------------

describe('resolveRightArrow', () => {
  it('expands a collapsed folder', () => {
    const f = row('f', { isFolder: true, isExpanded: false });
    expect(resolveRightArrow(f, [f], 0)).toEqual({ kind: 'expand', id: 'f' });
  });

  it('jumps to first child on an expanded folder', () => {
    const f = row('f', { isFolder: true, isExpanded: true });
    const c = row('f/c', { parentId: 'f', level: 1 });
    expect(resolveRightArrow(f, [f, c], 0)).toEqual({ kind: 'focus', id: 'f/c' });
  });

  it('no-op for an expanded folder with no children visible', () => {
    const f = row('f', { isFolder: true, isExpanded: true });
    expect(resolveRightArrow(f, [f], 0)).toEqual({ kind: 'noop' });
  });

  it('no-op for a leaf', () => {
    expect(resolveRightArrow(row('a'), rows, 0)).toEqual({ kind: 'noop' });
  });

  it('no-op when current is null', () => {
    expect(resolveRightArrow(null, rows, 0)).toEqual({ kind: 'noop' });
  });
});

describe('resolveLeftArrow', () => {
  it('collapses an expanded folder', () => {
    const f = row('f', { isFolder: true, isExpanded: true });
    expect(resolveLeftArrow(f)).toEqual({ kind: 'collapse', id: 'f' });
  });

  it('focuses parent for a leaf with a parent', () => {
    const c = row('f/c', { parentId: 'f' });
    expect(resolveLeftArrow(c)).toEqual({ kind: 'focus', id: 'f' });
  });

  it('no-op for a root leaf', () => {
    expect(resolveLeftArrow(row('root'))).toEqual({ kind: 'noop' });
  });
});

// ----------------------------------------------------------------------
// activation
// ----------------------------------------------------------------------

describe('resolveActivate', () => {
  it('toggles a folder — flags `willExpand` from current state', () => {
    const collapsed = row('f', { isFolder: true, isExpanded: false });
    expect(resolveActivate(collapsed)).toEqual({
      kind: 'toggle-folder',
      id: 'f',
      willExpand: true,
    });

    const expanded = row('f', { isFolder: true, isExpanded: true });
    expect(resolveActivate(expanded)).toEqual({
      kind: 'toggle-folder',
      id: 'f',
      willExpand: false,
    });
  });

  it('activates a leaf', () => {
    expect(resolveActivate(row('a'))).toEqual({ kind: 'activate-leaf', id: 'a' });
  });

  it('no-op for null', () => {
    expect(resolveActivate(null)).toEqual({ kind: 'noop' });
  });
});
