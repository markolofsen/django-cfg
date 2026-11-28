import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  CommitGraph,
  type Commit,
} from '.';

const now = Date.now();

const linearCommits: Commit[] = [
  {
    hash: 'abc1234',
    message: 'fix: resolve login redirect loop',
    author: { name: 'Alex Rivera' },
    date: new Date(now - 3 * 3600_000).toISOString(),
    parents: ['def5678'],
    refs: ['main'],
  },
  {
    hash: 'def5678',
    message: 'docs: update API reference',
    author: { name: 'Taylor Kim' },
    date: new Date(now - 12 * 3600_000).toISOString(),
    parents: ['ghi9012'],
  },
  {
    hash: 'ghi9012',
    message: 'feat: add dark mode toggle',
    author: { name: 'Sarah Chen' },
    date: new Date(now - 2 * 86400_000).toISOString(),
    parents: ['jkl3456'],
    tag: 'v1.2.0',
  },
  {
    hash: 'jkl3456',
    message: 'Initial commit',
    author: { name: 'Sarah Chen' },
    date: new Date(now - 7 * 86400_000).toISOString(),
    parents: [],
  },
];

const branchedCommits: Commit[] = [
  {
    hash: 'a1b2c3d',
    message: 'feat(auth): add OAuth2 support',
    author: { name: 'Sarah Chen' },
    date: new Date(now - 2 * 3600_000).toISOString(),
    parents: ['m1e2r3g'],
    refs: ['main', 'HEAD'],
    tag: 'v2.1.0',
  },
  {
    hash: 'm1e2r3g',
    message: "Merge branch 'feat/dashboard' into main",
    author: { name: 'Sarah Chen' },
    date: new Date(now - 6 * 3600_000).toISOString(),
    parents: ['f6e5d4c', 'd4a5s6h'],
  },
  {
    hash: 'd4a5s6h',
    message: 'feat: add analytics chart component',
    author: { name: 'Jordan Lee' },
    date: new Date(now - 8 * 3600_000).toISOString(),
    parents: ['w1i2p3'],
    refs: ['feat/dashboard'],
  },
  {
    hash: 'f6e5d4c',
    message: 'fix(api): handle rate limit headers',
    author: { name: 'Alex Rivera' },
    date: new Date(now - 18 * 3600_000).toISOString(),
    parents: ['4d5e6f1'],
  },
  {
    hash: 'w1i2p3',
    message: 'wip: dashboard layout skeleton',
    author: { name: 'Jordan Lee' },
    date: new Date(now - 2 * 86400_000).toISOString(),
    parents: ['4d5e6f1'],
  },
  {
    hash: '4d5e6f1',
    message: 'chore(deps): upgrade next to 15.5',
    author: { name: 'Sarah Chen' },
    date: new Date(now - 5 * 86400_000).toISOString(),
    parents: ['0a1b2c3'],
    tag: 'v2.0.0',
  },
  {
    hash: '0a1b2c3',
    message: 'Initial commit',
    author: { name: 'Sarah Chen' },
    date: new Date(now - 14 * 86400_000).toISOString(),
    parents: [],
  },
];

const meta = {
  title: 'Widgets/Charts/CommitGraph',
  component: CommitGraph,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Topological git graph rendered with SVG rails. Lane colors come from `useStylePresets()` so they follow the active theme preset — never raw hex. Pop-over uses the host `<UiProviders>` Popover primitive.',
      },
    },
  },
  argTypes: {
    truncateHash: { control: { type: 'number', min: 4, max: 12 } },
    railWidth: { control: { type: 'number', min: 16, max: 48 } },
  },
} satisfies Meta<typeof CommitGraph>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Linear: Story = {
  args: { commits: linearCommits },
};

export const Branched: Story = {
  args: { commits: branchedCommits },
};

export const NarrowRails: Story = {
  args: { commits: branchedCommits, railWidth: 18 },
};

export const Empty: Story = {
  args: { commits: [] },
};
