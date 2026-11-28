import type { Meta, StoryObj } from '@storybook/react-vite';
import { ApiRefTable, type ApiProp } from '.';

const SAMPLE_PROPS: ApiProp[] = [
  {
    name: 'title',
    type: 'string',
    required: true,
    description: 'Heading rendered above the column header strip.',
  },
  {
    name: 'props',
    type: 'ApiProp[]',
    required: true,
    description: 'Parameter / prop rows shown in the table body.',
    fullType: 'Array<{ name: string; type: string; required?: boolean; defaultValue?: string; description?: string; fullType?: string }>',
  },
  {
    name: 'variant',
    type: '"default" | "compact" | "verbose"',
    description: 'Visual density of each row.',
  },
  {
    name: 'count',
    type: 'number',
    description: 'How many rows to render before truncating.',
  },
  {
    name: 'expanded',
    type: 'boolean',
    description: 'Force every row into its expanded state.',
  },
  {
    name: 'onSelect',
    type: '(prop: ApiProp) => void',
    description: 'Fired when a row is activated via click or keyboard.',
  },
  {
    name: 'icon',
    type: 'ReactNode',
    description: 'Custom leading icon displayed alongside the title.',
  },
  {
    name: 'fallback',
    type: 'string | null',
    description: 'Rendered when `props` is empty.',
  },
];

const WITH_DEFAULTS: ApiProp[] = [
  {
    name: 'variant',
    type: '"default" | "compact" | "verbose"',
    defaultValue: '"default"',
    description: 'Visual density of each row.',
  },
  {
    name: 'count',
    type: 'number',
    defaultValue: '10',
  },
  {
    name: 'expanded',
    type: 'boolean',
    defaultValue: 'false',
  },
  {
    name: 'separator',
    type: 'string',
    defaultValue: '" | "',
    description: 'Token used to render unions in the type column.',
  },
  {
    name: 'fallback',
    type: 'ReactNode',
    defaultValue: 'null',
  },
];

const REQUIRED_ONLY: ApiProp[] = [
  {
    name: 'id',
    type: 'string',
    required: true,
    description: 'Stable identifier used as the React key.',
  },
  {
    name: 'value',
    type: 'string | number',
    required: true,
  },
  {
    name: 'onChange',
    type: '(next: string | number) => void',
    required: true,
    description: 'Controlled-input change handler.',
  },
];

const meta = {
  title: 'Widgets/Chat Dev/ApiRefTable',
  component: ApiRefTable,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'API reference / props table with per-token type colorization and expand-on-click rows. ' +
          'All type-tag colors map to semantic tokens (success / warning / info / destructive / muted / primary) ' +
          'plus one categorical via `--chart-3` for `enum` — never raw color scales.',
      },
    },
  },
} satisfies Meta<typeof ApiRefTable>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    title: 'ApiRefTable props',
    props: SAMPLE_PROPS,
  },
};

export const WithDefaults: Story = {
  args: {
    title: 'Defaults column',
    props: WITH_DEFAULTS,
  },
};

export const RequiredOnly: Story = {
  args: {
    title: 'Required props',
    props: REQUIRED_ONLY,
  },
};

export const Empty: Story = {
  args: {
    title: 'No props',
    props: [],
    emptyMessage: 'This component takes no props.',
  },
};
