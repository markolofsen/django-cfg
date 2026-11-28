import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, userEvent, within } from 'storybook/test';
import { TreeRoot } from '../Tree';

import {
  FS_TREE,
  FS_TREE_WITH_HIDDEN,
  LARGE_TREE,
  type FsNode,
} from './_fixtures';

const FsTree = TreeRoot<FsNode>;

const meta = {
  title: 'Widgets/Data/Tree/Interaction',
  tags: ['autodocs', 'contract'],
  parameters: { layout: 'centered', a11y: { test: 'error' } },
  component: FsTree,
  args: {
    data: FS_TREE,
    getItemName: (node) => node.data.name,
  },
} satisfies Meta<typeof FsTree>;
export default meta;

type Story = StoryObj<typeof meta>;

const ACTIVATION_MODES: Array<
  'single-click' | 'double-click' | 'single-click-preview'
> = ['single-click', 'double-click', 'single-click-preview'];

function ActivationModesHost() {
  const [log, setLog] = useState<string>('');
  return (
    <div className="flex flex-col gap-3">
      <div className="flex gap-3">
        {ACTIVATION_MODES.map((mode) => (
          <div key={mode} className="flex flex-col gap-1">
            <span className="text-[11px] font-medium text-muted-foreground">
              {mode}
            </span>
            <div className="h-72 w-64 rounded-md border bg-card">
              <TreeRoot<FsNode>
                data={FS_TREE}
                getItemName={(n) => n.data.name}
                activationMode={mode}
                initialExpandedIds={['src']}
                onActivate={(node, { preview }) =>
                  setLog(`${mode} → ${node.data.name} (preview=${preview})`)
                }
              />
            </div>
          </div>
        ))}
      </div>
      <p className="font-mono text-xs text-muted-foreground">
        last activation: {log || '(none)'}
      </p>
    </div>
  );
}

export const WithActivationModes: Story = {
  name: 'With Activation Modes',
  parameters: {
    docs: {
      description: {
        story:
          'Three side-by-side trees: `single-click` (default), `double-click` ' +
          '(file-manager style), and `single-click-preview` (VSCode / Cursor). ' +
          'Click a leaf in each — the log below records the activation payload.',
      },
    },
  },
  render: () => <ActivationModesHost />,
};

function HiddenFilterHost() {
  const [showHidden, setShowHidden] = useState(false);
  return (
    <div className="flex flex-col gap-3">
      <label className="flex items-center gap-2 text-xs">
        <input
          type="checkbox"
          checked={showHidden}
          onChange={(e) => setShowHidden(e.target.checked)}
        />
        <span>Show hidden (dot-prefixed) entries</span>
      </label>
      <div className="h-96 w-80 rounded-md border bg-card">
        <TreeRoot<FsNode>
          data={FS_TREE_WITH_HIDDEN}
          getItemName={(n) => n.data.name}
          initialExpandedIds={['project']}
          filterNode={(n) => showHidden || !n.data.name.startsWith('.')}
        />
      </div>
    </div>
  );
}

export const WithHiddenFilter: Story = {
  name: 'With Hidden Filter',
  parameters: {
    docs: {
      description: {
        story:
          '`filterNode` toggles visibility of dot-files (`.env`, `.git`, …). ' +
          'Excluded nodes (and their descendants) disappear from rendering, ' +
          'keyboard navigation, and search.',
      },
    },
  },
  render: () => <HiddenFilterHost />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.queryByText('.env')).not.toBeInTheDocument();
    await userEvent.click(
      canvas.getByRole('checkbox', {
        name: 'Show hidden (dot-prefixed) entries',
      }),
    );
    await expect(canvas.getByText('.env')).toBeVisible();
  },
};

export const WithSearch: Story = {
  name: 'With Search',
  parameters: {
    // TreeRoot currently places the search input inside role="tree".
    a11y: { test: 'todo' },
    docs: {
      description: {
        story:
          'Built-in search bar above the tree (`enableSearch`). Type to ' +
          'filter visible rows; matching segments get a primary-tinted ring.',
      },
    },
  },
  render: () => (
    <div className="h-[28rem] w-80 rounded-md border bg-card">
      <TreeRoot
        data={LARGE_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={LARGE_TREE.slice(0, 2).map((n) => n.id)}
        enableSearch
        appearance={{ density: 'compact' }}
      />
    </div>
  ),
};

const PERSIST_KEY = 'storybook.ui-tools.tree.persisted';

// `generation` keys the tree so clearing remounts it. TreeContext reads
// localStorage in a useMemo on `persistKey`, and its sync effect writes the live
// state straight back — a re-render alone restores the value just deleted.
function PersistedHost() {
  const [generation, setGeneration] = useState(0);
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="rounded border px-2 py-1 text-xs hover:bg-muted"
          onClick={() => {
            if (typeof window !== 'undefined') {
              window.localStorage.removeItem(PERSIST_KEY);
            }
            setGeneration((v) => v + 1);
          }}
        >
          Clear persisted state
        </button>
        <span className="font-mono text-[11px] text-muted-foreground">
          key: {PERSIST_KEY}
        </span>
      </div>
      <div className="h-96 w-80 rounded-md border bg-card">
        <TreeRoot<FsNode>
          key={generation}
          data={FS_TREE}
          getItemName={(n) => n.data.name}
          selectionMode="single"
          persistKey={PERSIST_KEY}
          persistSelection
        />
      </div>
    </div>
  );
}

export const Persisted: Story = {
  tags: ['manual'],
  parameters: {
    djangocfg: { storage: 'preserve' },
    docs: {
      description: {
        story:
          'Expanded set (and selection, if `persistSelection`) round-trips ' +
          'through localStorage under `persistKey`. Expand a few folders, ' +
          'reload the iframe — state is restored. The button below clears ' +
          'the stored value for this story.',
      },
    },
  },
  render: () => <PersistedHost />,
};
