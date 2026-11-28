import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  LazyCronScheduler as CronScheduler,
  type ScheduleType,
} from './lazy';

type TimeFormat = '12h' | '24h';
type CronSchedulerSize = 'default' | 'sm';

type HostProps = {
  initialValue: string;
  defaultType: ScheduleType;
  inline: boolean;
  size: CronSchedulerSize;
  showCronExpression: boolean;
  allowCopy: boolean;
  timeFormat: TimeFormat;
  disabled: boolean;
};

// ---------------------------------------------------------------------------
// Host: holds runtime cron state; re-mounts when `initialValue` changes.
// ---------------------------------------------------------------------------

function Host({
  initialValue,
  ...rest
}: HostProps) {
  const [cron, setCron] = useState(initialValue);
  return (
    <div className="w-[460px]">
      <CronScheduler value={cron} onChange={setCron} {...rest} />
    </div>
  );
}

/** Local lightweight 5-field cron split — utils are not part of the public package surface. */
function splitCron(expr: string): {
  minute: string;
  hour: string;
  dayOfMonth: string;
  month: string;
  dayOfWeek: string;
} | null {
  const parts = expr.trim().split(/\s+/);
  if (parts.length !== 5) return null;
  return {
    minute: parts[0]!,
    hour: parts[1]!,
    dayOfMonth: parts[2]!,
    month: parts[3]!,
    dayOfWeek: parts[4]!,
  };
}

function HostWithReadout(props: HostProps) {
  const [cron, setCron] = useState(props.initialValue);
  const parsed = splitCron(cron);
  return (
    <div className="w-[520px] space-y-3">
      <CronScheduler value={cron} onChange={setCron} {...props} />
      <div className="rounded-md border bg-muted/40 p-3 font-mono text-xs">
        <div>expr: <span className="text-foreground">{cron}</span></div>
        {parsed ? (
          <div className="mt-1 grid grid-cols-5 gap-2 text-[10px] text-muted-foreground">
            <div>min={parsed.minute}</div>
            <div>hr={parsed.hour}</div>
            <div>dom={parsed.dayOfMonth}</div>
            <div>mon={parsed.month}</div>
            <div>dow={parsed.dayOfWeek}</div>
          </div>
        ) : (
          <div className="mt-1 text-[10px] text-destructive">invalid (need 5 fields)</div>
        )}
      </div>
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/Cron/Scheduler',
  component: Host,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Compact cron expression builder. The default surface is a single popover trigger that reads the schedule as plain text ("Weekdays at 09:00") — the editor lives inside the popover. Pass `inline` for the legacy expanded layout. Controls drive initial config; runtime state lives inside the component.',
      },
    },
  },
  argTypes: {
    initialValue: {
      control: 'text',
      description: 'Initial cron expression (Unix 5-field format).',
      table: { category: 'Value' },
    },
    defaultType: {
      control: { type: 'inline-radio' },
      options: ['daily', 'weekly', 'monthly', 'custom'],
      table: { category: 'Tabs' },
    },
    timeFormat: {
      control: { type: 'inline-radio' },
      options: ['24h', '12h'],
      table: { category: 'Display' },
    },
    inline: {
      control: 'boolean',
      description: 'Render the editor expanded instead of behind a popover trigger.',
      table: { category: 'Display' },
    },
    size: {
      control: { type: 'inline-radio' },
      options: ['default', 'sm'],
      description:
        'Visual density. `sm` packs the fields tighter for narrow side panels / modals (~360-420px).',
      table: { category: 'Display' },
    },
    showCronExpression: { control: 'boolean', table: { category: 'Display' } },
    allowCopy: { control: 'boolean', table: { category: 'Display' } },
    disabled: { control: 'boolean', table: { category: 'Behaviour' } },
  },
} satisfies Meta<typeof Host>;

export default meta;

type Story = StoryObj<typeof meta>;

// ---------------------------------------------------------------------------
// Playground
// ---------------------------------------------------------------------------

export const Playground: Story = {
  args: {
    initialValue: '0 9 * * 1-5',
    defaultType: 'weekly',
    inline: false,
    size: 'default',
    showCronExpression: true,
    allowCopy: true,
    timeFormat: '24h',
    disabled: false,
  },
  render: (args) => (
    <Host key={args.initialValue + args.defaultType + args.size} {...args} />
  ),
};

// ---------------------------------------------------------------------------
// Curated presets
// ---------------------------------------------------------------------------

export const Default: Story = {
  args: { ...Playground.args!, initialValue: '0 9 * * *', defaultType: 'daily' },
  render: (args) => <Host key="default" {...args} />,
};

export const EveryMinute: Story = {
  args: { ...Playground.args!, initialValue: '* * * * *', defaultType: 'custom' },
  render: (args) => <Host key="every-minute" {...args} />,
};

export const Daily9AM: Story = {
  args: { ...Playground.args!, initialValue: '0 9 * * *', defaultType: 'daily' },
  render: (args) => <Host key="daily-9am" {...args} />,
};

export const Weekly: Story = {
  args: { ...Playground.args!, initialValue: '30 14 * * 1,3,5', defaultType: 'weekly' },
  render: (args) => <Host key="weekly" {...args} />,
};

export const Monthly: Story = {
  args: { ...Playground.args!, initialValue: '0 9 1,15 * *', defaultType: 'monthly' },
  render: (args) => <Host key="monthly" {...args} />,
};

export const Custom: Story = {
  args: {
    ...Playground.args!,
    initialValue: '*/15 9-17 * * 1-5',
    defaultType: 'custom',
    showCronExpression: true,
  },
  render: (args) => <Host key="custom" {...args} />,
};

export const Disabled: Story = {
  args: { ...Playground.args!, initialValue: '0 9 * * 1-5', disabled: true },
  render: (args) => <Host key="disabled" {...args} />,
};

export const WithReadout: Story = {
  args: {
    ...Playground.args!,
    initialValue: '*/15 9-17 * * 1-5',
    defaultType: 'custom',
    showCronExpression: true,
  },
  render: (args) => <HostWithReadout key="readout" {...args} />,
};

export const Inline: Story = {
  name: 'Inline (expanded)',
  args: {
    ...Playground.args!,
    initialValue: '0 9 * * 1-5',
    defaultType: 'weekly',
    inline: true,
    showCronExpression: true,
  },
  render: (args) => <Host key="inline" {...args} />,
};

// ---------------------------------------------------------------------------
// Compact size — tighter fields for narrow side panels / modals
// ---------------------------------------------------------------------------

export const CompactSize: Story = {
  name: 'Compact (size="sm")',
  parameters: {
    docs: {
      description: {
        story:
          'The `size="sm"` variant packs the schedule fields tighter so the ' +
          'scheduler fits inside narrow side panels and modals (~360-420px). ' +
          'Shown here in the default popover surface.',
      },
    },
  },
  args: {
    ...Playground.args!,
    initialValue: '0 9 * * 1-5',
    defaultType: 'weekly',
    size: 'sm',
    showCronExpression: true,
  },
  render: (args) => (
    <div className="w-[380px]">
      <CronScheduler
        key="compact-sm"
        value={args.initialValue}
        onChange={() => {}}
        defaultType={args.defaultType}
        size={args.size}
        inline={args.inline}
        showCronExpression={args.showCronExpression}
        allowCopy={args.allowCopy}
        timeFormat={args.timeFormat}
        disabled={args.disabled}
      />
    </div>
  ),
};

export const CompactSizeInline: Story = {
  name: 'Compact (size="sm", expanded)',
  parameters: {
    docs: {
      description: {
        story:
          'The compact `size="sm"` variant combined with `inline` — the editor ' +
          'is expanded with tighter fields, ideal for a settings drawer.',
      },
    },
  },
  args: {
    ...Playground.args!,
    initialValue: '*/15 9-17 * * 1-5',
    defaultType: 'custom',
    size: 'sm',
    inline: true,
    showCronExpression: true,
  },
  render: (args) => (
    <div className="w-[380px]">
      <CronScheduler
        key="compact-sm-inline"
        value={args.initialValue}
        onChange={() => {}}
        defaultType={args.defaultType}
        size={args.size}
        inline={args.inline}
        showCronExpression={args.showCronExpression}
        allowCopy={args.allowCopy}
        timeFormat={args.timeFormat}
        disabled={args.disabled}
      />
    </div>
  ),
};

// ---------------------------------------------------------------------------
// Size comparison — default vs sm side by side
// ---------------------------------------------------------------------------

export const SizeComparison: Story = {
  name: 'Size: default vs sm',
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: 'Default and compact (`sm`) density rendered side by side for comparison.',
      },
    },
  },
  args: {
    ...Playground.args!,
    initialValue: '0 9 * * 1-5',
    defaultType: 'weekly',
    showCronExpression: true,
    allowCopy: true,
  },
  render: ({ initialValue, ...rest }) => (
    <div className="flex flex-wrap gap-8">
      {(['default', 'sm'] as const).map((size) => (
        <div key={size} className="w-[380px] space-y-2">
          <div className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
            size=&quot;{size}&quot;
          </div>
          <CronScheduler {...rest} size={size} value={initialValue} onChange={() => {}} />
        </div>
      ))}
    </div>
  ),
};
