import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Copy, Pencil, Scissors, Trash2 } from 'lucide-react';
import { TreeRoot } from '../Tree';

import { FS_TREE, type FsNode } from './_fixtures';

const FsTree = TreeRoot<FsNode>;

const meta = {
  title: 'Widgets/Data/Tree/Context menu',
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

function ContextMenuHost() {
  const [lastAction, setLastAction] = useState<string>('');
  return (
    <div className="flex flex-col gap-3">
      <div className="h-96 w-80 rounded-md border bg-card">
        <TreeRoot<FsNode>
          data={FS_TREE}
          getItemName={(n) => n.data.name}
          initialExpandedIds={['src', 'src/components']}
          contextMenuActions={({ node, isFolder }) => [
            {
              id: 'rename',
              label: 'Rename',
              icon: Pencil,
              shortcut: '↵',
              onSelect: () => setLastAction(`Rename ${node.data.name}`),
            },
            {
              id: 'copy',
              label: 'Copy',
              icon: Copy,
              shortcut: '⌘C',
              onSelect: () => setLastAction(`Copy ${node.data.name}`),
            },
            {
              id: 'cut',
              label: 'Cut',
              icon: Scissors,
              shortcut: '⌘X',
              onSelect: () => setLastAction(`Cut ${node.data.name}`),
            },
            'separator',
            {
              id: 'delete',
              label: 'Delete',
              icon: Trash2,
              shortcut: '⌫',
              destructive: true,
              onSelect: () =>
                setLastAction(
                  `Delete ${isFolder ? 'folder' : 'file'} ${node.data.name}`,
                ),
            },
          ]}
        />
      </div>
      <p className="font-mono text-xs text-muted-foreground">
        last action: {lastAction || '(right-click a row)'}
      </p>
    </div>
  );
}

export const WithContextMenu: Story = {
  name: 'With Context Menu',
  parameters: {
    docs: {
      description: {
        story:
          'Declarative right-click menu via `contextMenuActions={(row) => [...]}`. ' +
          'Use `"separator"` strings between groups; mark dangerous items with ' +
          '`destructive: true`. The resolver receives `{ row, selectedNodes }` ' +
          '— `selectedNodes` reflects the active multi-selection (Tree first ' +
          'switches selection to the right-clicked row if it was outside). ' +
          'For full control (submenus, checkbox items, custom JSX) fall back ' +
          'to `renderContextMenu`.',
      },
    },
  },
  render: () => <ContextMenuHost />,
};
