import type { TreeNode } from '../../Tree';

export type Status = 'modified' | 'error' | 'clean';

export interface StatusNode {
  name: string;
  status?: Status;
}

export const STATUS_TREE: TreeNode<StatusNode>[] = [
  {
    id: 'src',
    data: { name: 'src' },
    children: [
      { id: 'a.ts', data: { name: 'a.ts', status: 'modified' } },
      { id: 'b.ts', data: { name: 'b.ts', status: 'error' } },
      { id: 'c.ts', data: { name: 'c.ts' } },
      { id: 'd.ts', data: { name: 'd.ts (vendored)' }, disabled: true },
    ],
  },
];
