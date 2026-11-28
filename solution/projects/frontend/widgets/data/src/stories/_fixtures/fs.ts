import { createDemoTree, type TreeNode } from '../../Tree';

export interface FsNode {
  name: string;
  ext?: string;
}

export const FS_TREE: TreeNode<FsNode>[] = [
  {
    id: 'src',
    data: { name: 'src' },
    children: [
      {
        id: 'src/components',
        data: { name: 'components' },
        children: [
          { id: 'src/components/Button.tsx', data: { name: 'Button.tsx', ext: 'tsx' } },
          { id: 'src/components/Card.tsx', data: { name: 'Card.tsx', ext: 'tsx' } },
          { id: 'src/components/Tree.tsx', data: { name: 'Tree.tsx', ext: 'tsx' } },
        ],
      },
      {
        id: 'src/hooks',
        data: { name: 'hooks' },
        children: [
          { id: 'src/hooks/useDebounce.ts', data: { name: 'useDebounce.ts', ext: 'ts' } },
          { id: 'src/hooks/useTheme.ts', data: { name: 'useTheme.ts', ext: 'ts' } },
        ],
      },
      {
        id: 'src/assets',
        data: { name: 'assets' },
        children: [
          { id: 'src/assets/logo.svg', data: { name: 'logo.svg', ext: 'svg' } },
          { id: 'src/assets/favicon.ico', data: { name: 'favicon.ico', ext: 'ico' } },
        ],
      },
      { id: 'src/index.ts', data: { name: 'index.ts', ext: 'ts' } },
    ],
  },
  {
    id: 'public',
    data: { name: 'public' },
    children: [{ id: 'public/robots.txt', data: { name: 'robots.txt', ext: 'txt' } }],
  },
  { id: 'package.json', data: { name: 'package.json', ext: 'json' } },
  { id: 'README.md', data: { name: 'README.md', ext: 'md' } },
];

/** File system with dot-files for the `WithHiddenFilter` story. */
export const FS_TREE_WITH_HIDDEN: TreeNode<FsNode>[] = [
  {
    id: 'project',
    data: { name: 'project' },
    children: [
      { id: '.env', data: { name: '.env' } },
      { id: '.gitignore', data: { name: '.gitignore' } },
      {
        id: '.git',
        data: { name: '.git' },
        children: [
          { id: '.git/HEAD', data: { name: 'HEAD' } },
          { id: '.git/config', data: { name: 'config' } },
        ],
      },
      { id: 'package.json', data: { name: 'package.json', ext: 'json' } },
      { id: 'README.md', data: { name: 'README.md', ext: 'md' } },
      {
        id: 'src',
        data: { name: 'src' },
        children: [
          { id: 'src/index.ts', data: { name: 'index.ts', ext: 'ts' } },
        ],
      },
    ],
  },
];

export const LARGE_TREE = createDemoTree({
  depth: 4,
  breadth: 4,
  rootPrefix: 'group',
});
