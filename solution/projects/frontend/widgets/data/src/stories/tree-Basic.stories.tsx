import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Briefcase,
  Code2,
  FileText,
  Folder,
  FolderOpen,
  Image as ImageIcon,
  User,
} from 'lucide-react';
import { TreeRoot } from '../Tree';

import {
  CATEGORY_TREE,
  FS_TREE,
  LARGE_TREE,
  ORG_TREE,
  type Category,
  type FsNode,
  type Person,
} from './_fixtures';

const FsTree = TreeRoot<FsNode>;

const meta = {
  title: 'Widgets/Data/Tree/Basic',
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

export const Default: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Minimal `TreeRoot` with only `data` + `getItemName`. Cozy density, ' +
          'single selection, search disabled, no indent guides.',
      },
    },
  },
  render: () => (
    <div className="h-96 w-80 rounded-md border bg-card">
      <TreeRoot<FsNode>
        data={FS_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={['src']}
      />
    </div>
  ),
};

export const Collapsed: Story = {
  render: () => (
    <div className="h-96 w-80 rounded-md border bg-card">
      <TreeRoot<FsNode>
        data={FS_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={[]}
      />
    </div>
  ),
};

export const FileSystem: Story = {
  render: () => (
    <div className="h-96 w-80 rounded-md border bg-card">
      <TreeRoot<FsNode>
        data={FS_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={['src', 'src/components']}
        showIndentGuides
      />
    </div>
  ),
};

export const OrgChart: Story = {
  render: () => (
    <div className="h-[28rem] w-96 rounded-md border bg-card">
      <TreeRoot<Person>
        data={ORG_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={['ceo', 'cto', 'eng-lead', 'design-lead', 'cfo']}
        renderIcon={({ isFolder }) =>
          isFolder ? (
            <Briefcase aria-hidden className="size-4 shrink-0 text-chart-1" />
          ) : (
            <User aria-hidden className="size-4 shrink-0 text-chart-2" />
          )
        }
        renderLabel={({ node }) => (
          <span className="flex min-w-0 items-baseline gap-2">
            <span className="truncate text-sm">{node.data.name}</span>
            <span className="truncate text-[11px] text-muted-foreground">
              {node.data.role}
            </span>
          </span>
        )}
      />
    </div>
  ),
};

export const Categories: Story = {
  render: () => (
    <div className="h-96 w-80 rounded-md border bg-card">
      <TreeRoot<Category>
        data={CATEGORY_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={['electronics', 'computers']}
        renderLabel={({ node }) => (
          <span className="flex min-w-0 flex-1 items-center justify-between gap-2">
            <span className="truncate">{node.data.name}</span>
            {typeof node.data.count === 'number' && (
              <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                {node.data.count}
              </span>
            )}
          </span>
        )}
      />
    </div>
  ),
};

export const LargeTree: Story = {
  render: () => (
    <div className="h-[32rem] w-96 rounded-md border bg-card">
      <TreeRoot
        data={LARGE_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={LARGE_TREE.slice(0, 2).map((n) => n.id)}
        enableSearch
        appearance={{ density: 'compact' }}
        showIndentGuides
      />
    </div>
  ),
};

export const WithIcons: Story = {
  render: () => (
    <div className="h-96 w-80 rounded-md border bg-card">
      <TreeRoot<FsNode>
        data={FS_TREE}
        getItemName={(n) => n.data.name}
        initialExpandedIds={['src', 'src/components', 'src/hooks', 'src/assets']}
        renderIcon={({ node, isFolder, isExpanded }) => {
          // File-type identity, not status: the blue names TypeScript and the
          // pink names an image, the way an editor's icon theme does. A
          // semantic token would claim a severity none of these carry.
          /* eslint-disable no-restricted-syntax */
          if (isFolder) {
            const Icon = isExpanded ? FolderOpen : Folder;
            return (
              <Icon aria-hidden className="size-4 shrink-0 text-amber-300/90" />
            );
          }
          const ext = node.data.ext;
          if (ext === 'tsx' || ext === 'ts')
            return <Code2 aria-hidden className="size-4 shrink-0 text-blue-400" />;
          if (ext === 'svg' || ext === 'ico')
            return <ImageIcon aria-hidden className="size-4 shrink-0 text-pink-400" />;
          /* eslint-enable no-restricted-syntax */
          return (
            <FileText aria-hidden className="size-4 shrink-0 text-muted-foreground/80" />
          );
        }}
      />
    </div>
  ),
};
