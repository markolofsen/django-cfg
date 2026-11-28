import type { Meta, StoryObj } from '@storybook/react-vite';
import { Tree, type TreeNode } from '../Tree';

/**
 * `Tree` — decomposed, slot-driven tree. Two looks shown here:
 *
 * - **FileExplorer** — the default file/folder look (icons, indent guides,
 *   VSCode active-bar).
 * - **ChatHistory** — a list-like preset for grouped histories: compact
 *   density, `hideLeafIcons`, no active-bar, no indent guides. This is the
 *   shape cmdop's chat sidebar uses (date buckets → sessions).
 */
// ── File-explorer demo data ──────────────────────────────────────────
interface FileNode {
  name: string;
}
const FILES: TreeNode<FileNode>[] = [
  {
    id: 'src',
    data: { name: 'src' },
    children: [
      { id: 'src/index.ts', data: { name: 'index.ts' } },
      {
        id: 'src/components',
        data: { name: 'components' },
        children: [
          { id: 'src/components/Button.tsx', data: { name: 'Button.tsx' } },
          { id: 'src/components/Card.tsx', data: { name: 'Card.tsx' } },
        ],
      },
    ],
  },
  { id: 'package.json', data: { name: 'package.json' } },
  { id: 'README.md', data: { name: 'README.md' } },
];

const FileTree = Tree<FileNode>;

const meta = {
  title: 'Widgets/Data/Tree/Overview',
  component: FileTree,
  parameters: { layout: 'padded' },
  args: {
    data: FILES,
    getItemName: (node) => node.data.name,
  },
} satisfies Meta<typeof FileTree>;
export default meta;

type Story = StoryObj<typeof meta>;

export const FileExplorer: Story = {
  args: {
    initialExpandedIds: ['src', 'src/components'],
    renderLabel: ({ node }) => <span>{node.data.name}</span>,
  },
  render: (args) => (
    <div className="w-72 rounded-lg border border-border">
      <FileTree {...args} />
    </div>
  ),
};

// ── Chat-history demo data (date buckets → sessions) ─────────────────
type ChatPayload =
  | { kind: 'group'; label: string }
  | { kind: 'session'; title: string; meta: string };

const CHAT: TreeNode<ChatPayload>[] = [
  {
    id: 'today',
    data: { kind: 'group', label: 'Today' },
    children: [
      { id: 't1', data: { kind: 'session', title: 'ping from chrome mcp smoke test', meta: '2 · 20m ago' } },
      { id: 't2', data: { kind: 'session', title: 'say hi in one word', meta: '22 · 3h ago' } },
    ],
  },
  {
    id: 'yesterday',
    data: { kind: 'group', label: 'Yesterday' },
    children: [
      { id: 'y1', data: { kind: 'session', title: 'что видишь в папке загрузок и можешь ли её открыть', meta: '80 · 1d ago' } },
      { id: 'y2', data: { kind: 'session', title: 'Привет', meta: '10 · 1d ago' } },
    ],
  },
  {
    id: 'older',
    data: { kind: 'group', label: 'Older' },
    children: [
      { id: 'o1', data: { kind: 'session', title: 'Покажи топ-5 процессов по CPU на сервере', meta: '2 · 5d ago' } },
    ],
  },
];

export const ChatHistory: Story = {
  render: () => (
    <div className="w-72 rounded-lg border border-border bg-sidebar">
      <Tree<ChatPayload>
        data={CHAT}
        getItemName={(n) =>
          n.data.kind === 'group' ? n.data.label : n.data.title
        }
        initialExpandedIds={['today', 'yesterday', 'older']}
        initialSelectedIds={['t2']}
        // `variant: "list"` = the macOS-sidebar / chat-history look
        // (no icons, auto-height rows, quiet selection). One prop.
        appearance={{ variant: 'list', indent: 10 }}
        showIndentGuides={false}
        contextMenuActions={(ctx) =>
          ctx.node.data.kind === 'session'
            ? [
                { id: 'rename', label: 'Rename', onSelect: () => {} },
                { id: 'copy', label: 'Copy title', onSelect: () => {} },
                'separator',
                { id: 'delete', label: 'Delete', destructive: true, onSelect: () => {} },
              ]
            : []
        }
        renderLabel={({ node }) =>
          node.data.kind === 'group' ? (
            <span className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground/80">
              {node.data.label}
            </span>
          ) : (
            <span className="flex min-w-0 flex-col">
              <span className="truncate text-[13px] leading-tight text-foreground">
                {node.data.title}
              </span>
              <span className="truncate text-[11px] leading-tight text-muted-foreground/80">
                {node.data.meta}
              </span>
            </span>
          )
        }
      />
    </div>
  ),
};
