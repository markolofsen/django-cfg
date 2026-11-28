import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { AlertCircle, CircleDot, Pencil, Trash2 } from 'lucide-react';
import { TreeRoot } from '../Tree';

import {
  FS_TREE,
  STATUS_TREE,
  type FsNode,
  type StatusNode,
} from './_fixtures';

const FsTree = TreeRoot<FsNode>;

const meta = {
  title: 'Widgets/Data/Tree/Appearance',
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

export const Densities: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Three density presets side-by-side: `compact`, `cozy` (default), ' +
          '`comfortable`. Row height, font size, and gap scale together.',
      },
    },
  },
  render: () => {
    const densities: Array<'compact' | 'cozy' | 'comfortable'> = [
      'compact',
      'cozy',
      'comfortable',
    ];
    return (
      <div className="flex gap-3">
        {densities.map((density) => (
          <div key={density} className="flex flex-col gap-1">
            <span className="text-[11px] font-medium text-muted-foreground">
              {density}
            </span>
            <div className="h-80 w-64 rounded-md border bg-card">
              <TreeRoot<FsNode>
                data={FS_TREE}
                getItemName={(n) => n.data.name}
                initialExpandedIds={['src', 'src/components']}
                appearance={{ density }}
              />
            </div>
          </div>
        ))}
      </div>
    );
  },
};

export const WithIndentGuides: Story = {
  name: 'With Indent Guides',
  parameters: {
    docs: {
      description: {
        story:
          'Opt-in vertical guides under expanded folders (`showIndentGuides`). ' +
          'Tweak `appearance.indentGuideOpacity` to taste.',
      },
    },
  },
  render: () => (
    <div className="h-96 w-80 rounded-md border bg-card">
      <TreeRoot<FsNode>
        data={FS_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={['src', 'src/components', 'src/hooks']}
        showIndentGuides
        appearance={{ indentGuideOpacity: 0.6 }}
      />
    </div>
  ),
};

export const WithStatus: Story = {
  name: 'With Status',
  parameters: {
    docs: {
      description: {
        story:
          'Per-row state communicated through `renderLabel`: modified files ' +
          'get a warning dot, errored files a destructive icon, and ' +
          '`node.disabled` is honoured by the engine (greyed + not selectable).',
      },
    },
  },
  render: () => (
    <div className="h-72 w-80 rounded-md border bg-card">
      <TreeRoot<StatusNode>
        data={STATUS_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={['src']}
        renderLabel={({ node }) => {
          const status = node.data.status;
          return (
            <span className="flex min-w-0 flex-1 items-center gap-2">
              <span className="truncate text-sm">{node.data.name}</span>
              {status === 'modified' && (
                <CircleDot
                  aria-label="modified"
                  className="size-3 shrink-0 text-warning"
                />
              )}
              {status === 'error' && (
                <AlertCircle
                  aria-label="error"
                  className="size-3 shrink-0 text-destructive"
                />
              )}
            </span>
          );
        }}
      />
    </div>
  ),
};

function ActionsHost() {
  const [lastAction, setLastAction] = useState<string>('');
  return (
    <div className="flex flex-col gap-3">
      <div className="h-96 w-80 rounded-md border bg-card">
        <TreeRoot<FsNode>
          data={FS_TREE}
          getItemName={(n) => n.data.name}
          initialExpandedIds={['src', 'src/components']}
          renderActions={({ node, isFolder }) =>
            isFolder ? null : (
              <span className="ml-auto flex items-center gap-1 opacity-0 group-hover/tree-row:opacity-100">
                <button
                  type="button"
                  aria-label={`Rename ${node.data.name}`}
                  className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                  onClick={(e) => {
                    e.stopPropagation();
                    setLastAction(`Rename ${node.data.name}`);
                  }}
                >
                  <Pencil className="size-3.5" />
                </button>
                <button
                  type="button"
                  aria-label={`Delete ${node.data.name}`}
                  className="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                  onClick={(e) => {
                    e.stopPropagation();
                    setLastAction(`Delete ${node.data.name}`);
                  }}
                >
                  <Trash2 className="size-3.5" />
                </button>
              </span>
            )
          }
        />
      </div>
      <p className="font-mono text-xs text-muted-foreground">
        last action: {lastAction || '(hover a file row)'}
      </p>
    </div>
  );
}

export const WithActions: Story = {
  name: 'With Actions',
  parameters: {
    docs: {
      description: {
        story:
          'Per-row action buttons appear on hover via `renderActions`. ' +
          'Rename / delete handlers receive the row meta. Buttons stop ' +
          'event propagation so they do not also activate the row.',
      },
    },
  },
  render: () => <ActionsHost />,
};
