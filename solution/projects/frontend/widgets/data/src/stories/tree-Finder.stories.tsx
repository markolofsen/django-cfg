import type { Meta, StoryObj } from '@storybook/react-vite';
import { FinderTree } from '../Tree';

import { FINDER_INITIAL, useFinderStore, type FsItem } from './_fixtures';

const FinderFsTree = FinderTree<FsItem>;

const meta = {
  title: 'Widgets/Data/Tree/Finder',
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
  component: FinderFsTree,
  args: {
    data: FINDER_INITIAL,
    getItemName: (node) => node.data.name,
  },
} satisfies Meta<typeof FinderFsTree>;
export default meta;

type Story = StoryObj<typeof meta>;

function FinderHost() {
  const { tree, adapter } = useFinderStore(FINDER_INITIAL);
  return (
    <div className="h-[28rem] w-80 rounded-md border bg-card">
      <FinderTree<FsItem>
        data={tree}
        getItemName={(n) => n.data.name}
        adapter={adapter}
      />
    </div>
  );
}

export const Finder: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Full Finder/Explorer preset: multi-select with shift/⌘ ranges, ' +
          'double-click activation, inline rename (F2 — auto-selects base ' +
          'without extension), Finder hotkeys (⌘⌫ ⌘D ⌘N ⌘⇧N ⌘C ⌘X ⌘V), ' +
          'cut/copy/paste with dimmed cut state, drag-and-drop reorder + ' +
          'move-into-folder, and a right-click "empty area" menu for ' +
          '`New file` / `New folder` / `Paste` at the root.\n\n' +
          'CRUD is wired through a tiny in-memory adapter — production ' +
          'hosts would point it at a backend (REST / WS / Wails → Go).',
      },
    },
  },
  render: () => <FinderHost />,
};
