import type { Meta, StoryObj } from '@storybook/react-vite';
import { CronPreview } from './lazy';

const meta = {
  title: 'Widgets/Forms/Cron/Preview',
  component: CronPreview,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Read-only sibling of `CronScheduler`. Renders a human-readable summary for a cron expression plus an optional list of upcoming run times. Use it in dashboards, list rows, and read-only schedule views where the editor is not needed.',
      },
    },
  },
  argTypes: {
    value: {
      control: 'text',
      description: 'Cron expression (standard 5-field format).',
    },
    title: {
      control: 'text',
      description: 'Optional heading shown above the summary.',
    },
    nextRuns: {
      control: { type: 'number', min: 0, max: 20, step: 1 },
      description: 'Number of upcoming run times to display. `0` hides the list.',
    },
    showExpression: {
      control: 'boolean',
      description: 'Show the raw cron expression alongside the summary.',
    },
  },
  args: {
    value: '0 9 * * 1-5',
    title: 'Daily standup reminder',
    nextRuns: 5,
    showExpression: true,
  },
  render: (args) => (
    <div className="w-[480px] max-w-full">
      <CronPreview {...args} />
    </div>
  ),
} satisfies Meta<typeof CronPreview>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

export const Weekdays: Story = {
  args: {
    value: '0 9 * * 1-5',
    title: 'Weekday morning job',
    nextRuns: 5,
  },
};

export const EveryFifteenMinutes: Story = {
  args: {
    value: '*/15 * * * *',
    title: 'High-frequency poller',
    nextRuns: 6,
  },
};

export const MonthlyReport: Story = {
  args: {
    value: '0 6 1 * *',
    title: 'Monthly report',
    nextRuns: 3,
  },
};

export const NoNextRuns: Story = {
  args: {
    value: '30 14 * * 0,6',
    title: 'Weekend digest',
    nextRuns: 0,
  },
};

export const HiddenExpression: Story = {
  args: {
    value: '0 12 * * *',
    title: 'Lunchtime ping',
    showExpression: false,
    nextRuns: 4,
  },
};

export const Invalid: Story = {
  args: {
    value: 'not a cron',
    title: undefined,
    nextRuns: 5,
  },
};
