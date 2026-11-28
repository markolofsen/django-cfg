import { useState } from 'react';

import type {
  TreeAdapter,
  TreeItemId,
  TreeMovePosition,
  TreeNode,
} from '../../Tree';

export interface FsItem {
  name: string;
}

export const FINDER_INITIAL: TreeNode<FsItem>[] = [
  {
    id: 'docs',
    data: { name: 'docs' },
    children: [
      { id: 'docs/readme.md', data: { name: 'readme.md' } },
      { id: 'docs/license.md', data: { name: 'license.md' } },
    ],
  },
  {
    id: 'src',
    data: { name: 'src' },
    children: [
      { id: 'src/index.ts', data: { name: 'index.ts' } },
      { id: 'src/utils.ts', data: { name: 'utils.ts' } },
    ],
  },
  { id: 'package.json', data: { name: 'package.json' } },
];

interface Row {
  id: TreeItemId;
  data: FsItem;
  parentId: TreeItemId | null;
  isFolder: boolean;
  order: number;
}

/**
 * Tiny in-memory store for the Finder story.
 *
 * A flat `Row[]` is easier to mutate than a recursive `TreeNode<T>[]`;
 * we project it back into a `TreeNode<FsItem>[]` on every render.
 *
 * Production hosts would normally drive this through their own data
 * layer (REST, WebSocket, Wails → Go, …) — this implementation only
 * exists so the story is fully interactive without a backend.
 */
export function useFinderStore(initial: TreeNode<FsItem>[]) {
  const [rows, setRows] = useState<Row[]>(() => {
    const out: Row[] = [];
    let counter = 0;
    const walk = (nodes: TreeNode<FsItem>[], parentId: TreeItemId | null) => {
      for (const n of nodes) {
        out.push({
          id: n.id,
          data: n.data,
          parentId,
          isFolder: Array.isArray(n.children) || !!n.isFolder,
          order: counter++,
        });
        if (Array.isArray(n.children)) walk(n.children, n.id);
      }
    };
    walk(initial, null);
    return out;
  });

  const tree = projectTree(rows);

  let nextId = rows.length;
  const mintId = (): TreeItemId =>
    `node-${++nextId}-${Math.random().toString(36).slice(2, 6)}`;

  const collectDescendants = (id: TreeItemId, acc: Set<TreeItemId>) => {
    acc.add(id);
    for (const r of rows) if (r.parentId === id) collectDescendants(r.id, acc);
  };

  const resolveDropParent = (
    target: TreeNode<FsItem> | null,
    position: TreeMovePosition,
  ): TreeItemId | null => {
    if (!target) return null;
    const targetRow = rows.find((r) => r.id === target.id);
    if (!targetRow) return null;
    return position === 'inside' && targetRow.isFolder
      ? targetRow.id
      : targetRow.parentId;
  };

  const adapter: TreeAdapter<FsItem> = {
    remove: async (nodes) => {
      const doomed = new Set<TreeItemId>();
      for (const n of nodes) collectDescendants(n.id, doomed);
      setRows((rs) => rs.filter((r) => !doomed.has(r.id)));
    },
    rename: async (node, name) => {
      setRows((rs) =>
        rs.map((r) => (r.id === node.id ? { ...r, data: { ...r.data, name } } : r)),
      );
    },
    createFile: async (parent, name) => {
      setRows((rs) => [
        ...rs,
        {
          id: mintId(),
          data: { name },
          parentId: parent?.id ?? null,
          isFolder: false,
          order: rs.length,
        },
      ]);
    },
    createFolder: async (parent, name) => {
      setRows((rs) => [
        ...rs,
        {
          id: mintId(),
          data: { name },
          parentId: parent?.id ?? null,
          isFolder: true,
          order: rs.length,
        },
      ]);
    },
    duplicate: async (nodes) => {
      setRows((rs) => {
        const next = [...rs];
        let order = rs.length;
        for (const n of nodes) {
          const src = rs.find((r) => r.id === n.id);
          if (!src) continue;
          next.push({
            id: mintId(),
            data: { ...src.data, name: `${src.data.name} copy` },
            parentId: src.parentId,
            isFolder: src.isFolder,
            order: order++,
          });
        }
        return next;
      });
    },
    move: async (nodes, target, position) => {
      const nodeIds = new Set(nodes.map((n) => n.id));
      const nextParent = resolveDropParent(target, position);
      setRows((rs) =>
        rs.map((r) => (nodeIds.has(r.id) ? { ...r, parentId: nextParent } : r)),
      );
    },
    copy: async (nodes, target, position) => {
      const nextParent = resolveDropParent(target, position);
      setRows((rs) => {
        let order = rs.length;
        const copies: Row[] = nodes.map((n) => {
          const src = rs.find((r) => r.id === n.id)!;
          return {
            id: mintId(),
            data: { ...src.data },
            parentId: nextParent,
            isFolder: src.isFolder,
            order: order++,
          };
        });
        return [...rs, ...copies];
      });
    },
    validateName: (name) =>
      name.trim().length === 0 ? 'Name cannot be empty' : null,
  };

  return { tree, adapter };
}

function projectTree(rows: Row[]): TreeNode<FsItem>[] {
  const byParent = new Map<TreeItemId | null, Row[]>();
  for (const r of [...rows].sort((a, b) => a.order - b.order)) {
    const arr = byParent.get(r.parentId) ?? [];
    arr.push(r);
    byParent.set(r.parentId, arr);
  }
  const build = (parentId: TreeItemId | null): TreeNode<FsItem>[] => {
    const list = byParent.get(parentId) ?? [];
    return list.map<TreeNode<FsItem>>((r) => ({
      id: r.id,
      data: r.data,
      isFolder: r.isFolder,
      children: r.isFolder ? build(r.id) : undefined,
    }));
  };
  return build(null);
}
