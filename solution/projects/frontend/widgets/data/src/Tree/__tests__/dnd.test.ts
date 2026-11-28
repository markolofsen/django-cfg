import { describe, expect, it } from 'vitest';

import { defaultCanDrop, resolveDropZone } from '../data/dnd';
import type { TreeNode } from '../types';

const rowRect = { top: 0, bottom: 30, height: 30 };

describe('resolveDropZone (folder targets)', () => {
  it('returns `before` in the top third', () => {
    expect(
      resolveDropZone({ pointerY: 5, rowRect, isFolder: true }),
    ).toBe('before');
  });

  it('returns `inside` in the middle third', () => {
    expect(
      resolveDropZone({ pointerY: 15, rowRect, isFolder: true }),
    ).toBe('inside');
  });

  it('returns `after` in the bottom third', () => {
    expect(
      resolveDropZone({ pointerY: 25, rowRect, isFolder: true }),
    ).toBe('after');
  });
});

describe('resolveDropZone (leaf targets)', () => {
  it('splits leaves in half: before / after', () => {
    expect(
      resolveDropZone({ pointerY: 10, rowRect, isFolder: false }),
    ).toBe('before');
    expect(
      resolveDropZone({ pointerY: 20, rowRect, isFolder: false }),
    ).toBe('after');
  });

  it('never returns `inside` for a leaf', () => {
    // Sweep the row — none of these should report `inside`.
    for (let y = 0; y <= 30; y++) {
      expect(
        resolveDropZone({ pointerY: y, rowRect, isFolder: false }),
      ).not.toBe('inside');
    }
  });
});

describe('resolveDropZone (degenerate row)', () => {
  it('falls back to a sensible default when height is zero', () => {
    expect(
      resolveDropZone({
        pointerY: 5,
        rowRect: { top: 0, bottom: 0, height: 0 },
        isFolder: false,
      }),
    ).toBe('after');
  });
});

// ----------------------------------------------------------------------
// defaultCanDrop
// ----------------------------------------------------------------------

interface FsItem {
  name: string;
}

const folder: TreeNode<FsItem> = {
  id: 'folder',
  data: { name: 'folder' },
  isFolder: true,
  children: [
    { id: 'child', data: { name: 'child' } },
    {
      id: 'nested-folder',
      data: { name: 'nested' },
      isFolder: true,
      children: [{ id: 'grandchild', data: { name: 'gc' } }],
    },
  ],
};

const leaf: TreeNode<FsItem> = { id: 'leaf', data: { name: 'leaf' } };

const lookup = new Map<string, TreeNode<FsItem>>();
function indexNodes(node: TreeNode<FsItem>) {
  lookup.set(node.id, node);
  if (Array.isArray(node.children)) node.children.forEach(indexNodes);
}
indexNodes(folder);
indexNodes(leaf);

describe('defaultCanDrop', () => {
  it('allows a drop on the root (null target)', () => {
    expect(
      defaultCanDrop({
        source: [leaf],
        target: null,
        position: 'inside',
        getNodeById: (id) => lookup.get(id),
      }),
    ).toBe(true);
  });

  it('rejects dropping a node onto itself', () => {
    expect(
      defaultCanDrop({
        source: [folder],
        target: folder,
        position: 'inside',
        getNodeById: (id) => lookup.get(id),
      }),
    ).toBe(false);
  });

  it('rejects `inside` drop on a leaf', () => {
    expect(
      defaultCanDrop({
        source: [folder],
        target: leaf,
        position: 'inside',
        getNodeById: (id) => lookup.get(id),
      }),
    ).toBe(false);
  });

  it('allows `before`/`after` drop on a leaf', () => {
    expect(
      defaultCanDrop({
        source: [folder],
        target: leaf,
        position: 'before',
        getNodeById: (id) => lookup.get(id),
      }),
    ).toBe(true);
  });

  it('rejects dropping a folder into its own descendant', () => {
    const nested = lookup.get('nested-folder')!;
    expect(
      defaultCanDrop({
        source: [folder],
        target: nested,
        position: 'inside',
        getNodeById: (id) => lookup.get(id),
      }),
    ).toBe(false);
  });

  it('rejects an empty source list', () => {
    expect(
      defaultCanDrop({
        source: [],
        target: null,
        position: 'inside',
        getNodeById: (id) => lookup.get(id),
      }),
    ).toBe(false);
  });
});
