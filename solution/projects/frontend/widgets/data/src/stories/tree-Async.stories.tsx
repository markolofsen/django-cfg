import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  TreeContent,
  TreeProvider,
  TreeRoot,
  useTreeActions,
  type TreeNode,
} from '../Tree';

import { FS_TREE, type FsNode } from './_fixtures';

const FsTree = TreeRoot<FsNode>;

const meta = {
  title: 'Widgets/Data/Tree/Async',
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
  component: FsTree,
  args: {
    data: FS_TREE,
    getItemName: (node) => node.data.name,
  },
} satisfies Meta<typeof FsTree>;
export default meta;

type Story = StoryObj<typeof meta>;

const ASYNC_ROOTS: TreeNode<FsNode>[] = [
  { id: 'remote-a', data: { name: 'remote-a' }, isFolder: true },
  { id: 'remote-b', data: { name: 'remote-b' }, isFolder: true },
];

async function fakeLoadChildren(node: TreeNode<FsNode>): Promise<TreeNode<FsNode>[]> {
  await new Promise((r) => setTimeout(r, 400));
  return [
    { id: `${node.id}/folder`, data: { name: 'subfolder' }, isFolder: true },
    { id: `${node.id}/index.ts`, data: { name: 'index.ts', ext: 'ts' } },
    { id: `${node.id}/README.md`, data: { name: 'README.md', ext: 'md' } },
  ];
}

export const AsyncLazyChildren: Story = {
  name: 'Async Lazy Children',
  parameters: {
    docs: {
      description: {
        story:
          'Folders without inline `children` resolve through `loadChildren` on ' +
          'first expand. The provider caches results and de-duplicates ' +
          'concurrent fetches per id; subsequent expand/collapse is instant.',
      },
    },
  },
  render: () => (
    <div className="h-72 w-80 rounded-md border bg-card">
      <TreeRoot<FsNode>
        data={ASYNC_ROOTS}
        getItemName={(n) => n.data.name}
        loadChildren={fakeLoadChildren}
      />
    </div>
  ),
};

function ExpandCollapseToolbar() {
  const { expandAll, collapseAll } = useTreeActions();
  return (
    <div className="flex items-center gap-2 border-b bg-muted/40 px-2 py-1.5">
      <button
        type="button"
        onClick={expandAll}
        className="rounded px-2 py-0.5 text-xs hover:bg-muted"
      >
        Expand all
      </button>
      <button
        type="button"
        onClick={collapseAll}
        className="rounded px-2 py-0.5 text-xs hover:bg-muted"
      >
        Collapse all
      </button>
    </div>
  );
}

export const ExpandCollapseAll: Story = {
  name: 'Expand / Collapse All',
  parameters: {
    docs: {
      description: {
        story:
          'Composition mode: drop a `TreeProvider`, a custom toolbar that ' +
          'calls `useTreeActions().expandAll() / collapseAll()`, and the ' +
          'default `TreeContent` below.',
      },
    },
  },
  render: () => (
    <div className="flex h-96 w-80 flex-col overflow-hidden rounded-md border bg-card">
      <TreeProvider<FsNode>
        data={FS_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={['src']}
      >
        <ExpandCollapseToolbar />
        <div className="min-h-0 flex-1">
          <TreeContent />
        </div>
      </TreeProvider>
    </div>
  ),
};
