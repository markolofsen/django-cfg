'use client';

import type { TreeNode } from '../types';

export interface DemoNode {
  name: string;
}

/**
 * Build a deterministic synthetic tree for stories and tests.
 *
 * @example
 *   const data = createDemoTree({ depth: 4, breadth: 3 });
 *   <TreeRoot data={data} getItemName={(n) => n.data.name} />
 */
export function createDemoTree({
  depth = 3,
  breadth = 4,
  rootPrefix = 'node',
}: {
  depth?: number;
  breadth?: number;
  rootPrefix?: string;
} = {}): TreeNode<DemoNode>[] {
  const make = (id: string, name: string, level: number): TreeNode<DemoNode> => {
    if (level >= depth) {
      return { id, data: { name } };
    }
    const children: TreeNode<DemoNode>[] = [];
    for (let i = 0; i < breadth; i++) {
      const childId = `${id}/${i}`;
      children.push(make(childId, `${name}-${i}`, level + 1));
    }
    return { id, data: { name }, children };
  };

  const roots: TreeNode<DemoNode>[] = [];
  for (let i = 0; i < breadth; i++) {
    roots.push(make(`${rootPrefix}-${i}`, `${rootPrefix} ${i}`, 1));
  }
  return roots;
}
