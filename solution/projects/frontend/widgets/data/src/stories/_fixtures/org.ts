import type { TreeNode } from '../../Tree';

export interface Person {
  name: string;
  role: string;
}

export const ORG_TREE: TreeNode<Person>[] = [
  {
    id: 'ceo',
    data: { name: 'Alex Morgan', role: 'CEO' },
    children: [
      {
        id: 'cto',
        data: { name: 'Priya Patel', role: 'CTO' },
        children: [
          {
            id: 'eng-lead',
            data: { name: 'Diego Ramos', role: 'Eng Lead' },
            children: [
              { id: 'eng-1', data: { name: 'Mei Chen', role: 'Frontend' } },
              { id: 'eng-2', data: { name: 'Lukas Weber', role: 'Backend' } },
              { id: 'eng-3', data: { name: 'Nina Kovac', role: 'DevOps' } },
            ],
          },
          {
            id: 'design-lead',
            data: { name: 'Sara Lindqvist', role: 'Design Lead' },
            children: [
              { id: 'des-1', data: { name: 'Tomás Pinto', role: 'Product Designer' } },
              { id: 'des-2', data: { name: 'Yuki Tanaka', role: 'Brand Designer' } },
            ],
          },
        ],
      },
      {
        id: 'cfo',
        data: { name: 'Robert Hayes', role: 'CFO' },
        children: [
          { id: 'fin-1', data: { name: 'Anna Petrov', role: 'Controller' } },
          { id: 'fin-2', data: { name: 'Hassan Ali', role: 'Analyst' } },
        ],
      },
    ],
  },
];
