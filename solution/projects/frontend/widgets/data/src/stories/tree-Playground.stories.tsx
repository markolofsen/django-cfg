import type { Meta, StoryObj } from '@storybook/react-vite';
import { TreeRoot, type TreeSelectionMode } from '../Tree';

import { FS_TREE, type FsNode } from './_fixtures';

/**
 * The playground's two synthetic knobs — `defaultExpanded` and `density` — are
 * not `TreeRoot` props: one derives `initialExpandedIds`, the other nests into
 * `appearance`. They live on a real component rather than on a story-only args
 * type so `satisfies Meta<typeof TreePlayground>` actually checks them.
 */
interface TreePlaygroundProps {
  selectionMode: TreeSelectionMode;
  /** Expand all top-level folders by default. */
  defaultExpanded: boolean;
  showIndentGuides: boolean;
  enableSearch: boolean;
  density: 'compact' | 'cozy' | 'comfortable';
}

function TreePlayground({
  selectionMode,
  defaultExpanded,
  showIndentGuides,
  enableSearch,
  density,
}: TreePlaygroundProps) {
  const expanded = defaultExpanded
    ? FS_TREE.filter((n) => n.children?.length).map((n) => n.id)
    : [];
  return (
    <div className="h-96 w-80 rounded-md border bg-card">
      <TreeRoot<FsNode>
        data={FS_TREE}
        getItemName={(n) => n.data.name}
        selectionMode={selectionMode}
        initialExpandedIds={expanded}
        showIndentGuides={showIndentGuides}
        enableSearch={enableSearch}
        appearance={{ density }}
      />
    </div>
  );
}

const meta = {
  title: 'Widgets/Data/Tree/Playground',
  component: TreePlayground,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Every Tree knob exposed as a Storybook control. Use this story to ' +
          'feel out density / selection / indent guides without writing code.',
      },
    },
  },
  argTypes: {
    selectionMode: {
      control: { type: 'inline-radio' },
      options: ['none', 'single', 'multiple'],
      description: 'none | single | multiple. `multiple` enables multi-select.',
    },
    defaultExpanded: {
      control: 'boolean',
      description: 'Expand all top-level folders by default.',
    },
    showIndentGuides: {
      control: 'boolean',
      description: 'Render vertical indent guides under expanded folders.',
    },
    enableSearch: { control: 'boolean' },
    density: {
      control: { type: 'inline-radio' },
      options: ['compact', 'cozy', 'comfortable'],
    },
  },
  args: {
    selectionMode: 'single',
    defaultExpanded: true,
    showIndentGuides: false,
    enableSearch: false,
    density: 'cozy',
  },
} satisfies Meta<typeof TreePlayground>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Playground: Story = {};
