import type { Meta, StoryObj } from '@storybook/react-vite';
import { LazyJsonTree as JsonTree } from '../JsonTree';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const SIMPLE = {
  user: {
    id: 'u_42',
    name: 'Mark',
    roles: ['admin', 'editor'],
    profile: { bio: 'Building djangocfg.', joined: '2024-09-01' },
  },
  flags: { beta: true, newAuth: false },
  counts: [1, 1, 2, 3, 5, 8, 13],
};

const NESTED = {
  a: { b: { c: { d: { e: { f: { g: { h: 'deep value' } } } } } } },
};

const MIXED_TYPES = {
  string: 'hello',
  number: 42,
  float: 3.14159,
  boolean: true,
  nullValue: null,
  emptyArray: [],
  emptyObject: {},
  date: new Date('2024-01-15T10:30:00Z').toISOString(),
  longString:
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
  url: 'https://djangocfg.dev/docs',
  tags: ['typescript', 'react', 'storybook'],
  nested: {
    coords: { lat: 51.5074, lng: -0.1278 },
    metric: { uptime: 99.95, errors: 0 },
  },
};

const API_RESPONSE = {
  status: 200,
  data: {
    items: [
      { id: 1, title: 'First', tags: ['a', 'b'] },
      { id: 2, title: 'Second', tags: ['c'] },
    ],
    pagination: { page: 1, total: 42 },
  },
  meta: { fetchedAt: '2024-01-20T14:45:00Z' },
};

const LARGE = {
  list: Array.from({ length: 1000 }, (_, i) => ({
    id: i,
    slug: `item-${i.toString().padStart(4, '0')}`,
    active: i % 3 !== 0,
    score: Math.round(Math.random() * 1000) / 10,
  })),
};

// ---------------------------------------------------------------------------
// Meta
// ---------------------------------------------------------------------------

const meta = {
  title: 'Widgets/Data/JSON Tree',
  component: JsonTree,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'JSON viewer with expand/collapse, copy, download. Public props: `data`, `title`, `toolbar`, `actions`, `defaultExpandedDepth`, `size`, `bordered`.',
      },
    },
  },
} satisfies Meta<typeof JsonTree>;

export default meta;
type Story = StoryObj<typeof meta>;

// ---------------------------------------------------------------------------
// Playground
// ---------------------------------------------------------------------------

export const Playground: Story = {
  args: {
    data: API_RESPONSE,
    title: 'Response',
    toolbar: 'always',
    actions: ['search', 'expand', 'copy', 'download'],
    defaultExpandedDepth: 2,
    size: 'sm',
    bordered: true,
  },
  argTypes: {
    data: { control: false, table: { category: 'Data' } },
    title: { control: 'text', table: { category: 'Data' } },
    toolbar: {
      control: 'inline-radio',
      options: ['auto', 'always', 'never'],
      table: { category: 'Toolbar' },
    },
    actions: {
      control: 'check',
      options: ['search', 'expand', 'copy', 'download'],
      table: { category: 'Toolbar' },
    },
    defaultExpandedDepth: {
      control: { type: 'number', min: 0, max: 10 },
      table: { category: 'Rendering' },
    },
    size: {
      control: 'inline-radio',
      options: ['sm', 'md', 'lg'],
      table: { category: 'Rendering' },
    },
    bordered: { control: 'boolean', table: { category: 'Rendering' } },
  },
  render: (args) => (
    <div className="w-[720px]">
      <JsonTree {...args} />
    </div>
  ),
};

// ---------------------------------------------------------------------------
// Curated presets
// ---------------------------------------------------------------------------

export const Simple: Story = {
  args: { data: SIMPLE },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const Large: Story = {
  args: { data: LARGE, title: '1000 items', defaultExpandedDepth: 1 },
  render: (args) => (
    <div className="h-[560px] w-[720px] overflow-auto">
      <JsonTree {...args} />
    </div>
  ),
};

export const Nested: Story = {
  args: { data: NESTED, defaultExpandedDepth: true },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const MixedTypes: Story = {
  args: { data: MIXED_TYPES, title: 'All value kinds' },
  render: (args) => (
    <div className="w-[720px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const NoToolbar: Story = {
  args: { data: API_RESPONSE, toolbar: 'never' },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const HoverToolbar: Story = {
  args: { data: SIMPLE, toolbar: 'auto' },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const CollapsedByDefault: Story = {
  args: { data: API_RESPONSE, title: 'Tap to expand', defaultExpandedDepth: 0 },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const FullyExpanded: Story = {
  args: { data: API_RESPONSE, defaultExpandedDepth: true },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const SizeLarge: Story = {
  name: 'Size = lg (presentation)',
  args: { data: SIMPLE, size: 'lg' },
  render: (args) => (
    <div className="w-[720px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const Flush: Story = {
  name: 'bordered={false} (flush in host pane)',
  args: { data: SIMPLE, bordered: false },
  render: (args) => (
    <div className="w-[640px] rounded-md border border-border p-4">
      <JsonTree {...args} />
    </div>
  ),
};

// ---------------------------------------------------------------------------
// Toolbar composition
// ---------------------------------------------------------------------------

export const AlwaysToolbar: Story = {
  name: 'Toolbar always visible (debug mode)',
  args: { data: API_RESPONSE, toolbar: 'always' },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const WithDownload: Story = {
  name: 'With download action',
  // `download` is opt-in: it makes sense for in-memory data and not for a
  // viewer over a file the host already has on disk.
  args: {
    data: API_RESPONSE,
    actions: ['search', 'expand', 'copy', 'download'],
    toolbar: 'always',
  },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const SearchOnly: Story = {
  name: 'Search only',
  args: { data: API_RESPONSE, actions: ['search'], toolbar: 'always' },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};

export const Primitive: Story = {
  name: 'Primitive value',
  // The degenerate input: `data` is typed `unknown`, so a bare string is legal
  // and must still render as a tree of one labelled row.
  args: { data: 'just a plain string', rootName: 'message' },
  render: (args) => (
    <div className="w-[640px]">
      <JsonTree {...args} />
    </div>
  ),
};
