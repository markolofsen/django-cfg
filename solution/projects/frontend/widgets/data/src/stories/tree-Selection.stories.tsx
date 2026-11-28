import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { TreeRoot, type TreeItemId } from '../Tree';

import { FS_TREE, type FsNode } from './_fixtures';

const FsTree = TreeRoot<FsNode>;

const meta = {
  title: 'Widgets/Data/Tree/Selection',
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

function SelectionHost(props: {
  selectionMode: 'single' | 'multiple';
  expanded: TreeItemId[];
  readout: (selected: TreeItemId[]) => string;
  readoutFirst?: boolean;
}) {
  const [selected, setSelected] = useState<TreeItemId[]>([]);
  const readout = (
    <p className="font-mono text-xs text-muted-foreground">
      {props.readout(selected)}
    </p>
  );
  return (
    <div className="flex flex-col gap-3">
      {props.readoutFirst ? readout : null}
      <div className="h-96 w-80 rounded-md border bg-card">
        <TreeRoot<FsNode>
          data={FS_TREE}
          getItemName={(n) => n.data.name}
          selectionMode={props.selectionMode}
          initialExpandedIds={props.expanded}
          onSelectionChange={setSelected}
        />
      </div>
      {props.readoutFirst ? null : readout}
    </div>
  );
}

export const Selectable: Story = {
  render: () => (
    <SelectionHost
      selectionMode="single"
      expanded={['src', 'src/components']}
      readout={(s) => `selected: ${s.join(', ') || '(none)'}`}
    />
  ),
};

export const MultiSelect: Story = {
  render: () => (
    <SelectionHost
      selectionMode="multiple"
      expanded={['src', 'src/components', 'src/hooks']}
      readout={(s) => `${s.length} selected: ${s.join(', ') || '(none)'}`}
    />
  ),
};

export const MultiSelectShiftRange: Story = {
  name: 'Multi-Select (Shift Range)',
  parameters: {
    docs: {
      description: {
        story:
          'Multi-select with Finder semantics. Click a row to set the anchor. ' +
          'Shift-click another row to select the range between them. ⌘/Ctrl-' +
          'click toggles a single row. Shift+↑/↓ extends the range from the ' +
          'anchor. ⌘/Ctrl+A selects every visible row. Esc clears.',
      },
    },
  },
  render: () => (
    <SelectionHost
      selectionMode="multiple"
      expanded={['src', 'src/components']}
      readout={(s) => `selected: [${s.join(', ')}]`}
      readoutFirst
    />
  ),
};
