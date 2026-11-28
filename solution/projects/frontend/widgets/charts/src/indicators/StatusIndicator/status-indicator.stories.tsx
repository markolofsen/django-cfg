import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  StatusIndicator,
  type Status,
  type StatusTone,
} from '.';

const STATUSES: Status[] = [
  'operational',
  'degraded',
  'partial-outage',
  'major-outage',
  'maintenance',
  'incident',
  'unknown',
];

const meta = {
  title: 'Widgets/Charts/StatusIndicator',
  component: StatusIndicator,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Operational status badge. Semantic tokens only (success / warning / destructive / info / muted) — colors follow the active theme preset. Pulsing halo on live statuses uses Tailwind `animate-ping`, no framer-motion.',
      },
    },
  },
  argTypes: {
    status: { control: 'select', options: STATUSES },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    tone: {
      control: 'select',
      options: ['success', 'warning', 'destructive', 'info', 'muted'] satisfies StatusTone[],
    },
    pulse: { control: 'boolean' },
    label: { control: 'text' },
  },
} satisfies Meta<typeof StatusIndicator>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { status: 'operational' },
};

export const AllStatuses: Story = {
  args: { status: 'operational' },
  render: () => (
    <div className="flex flex-wrap gap-3">
      {STATUSES.map((status) => (
        <StatusIndicator key={status} status={status} />
      ))}
    </div>
  ),
};

export const Sizes: Story = {
  args: { status: 'incident' },
  render: () => (
    <div className="flex flex-wrap items-center gap-3">
      <StatusIndicator status="incident" size="sm" />
      <StatusIndicator status="incident" size="md" />
      <StatusIndicator status="incident" size="lg" />
    </div>
  ),
};

export const CustomToneAndLabel: Story = {
  args: {
    status: 'operational',
    label: 'API v3.1 live',
    tone: 'info',
  },
};

export const PulseDisabled: Story = {
  args: { status: 'incident', pulse: false },
};
