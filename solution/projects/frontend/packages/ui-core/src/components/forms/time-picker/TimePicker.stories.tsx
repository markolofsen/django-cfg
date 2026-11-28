import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { TimePicker } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/TimePicker',
  component: TimePicker,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A time picker with popover selectors for hours and minutes, supporting 12/24-hour formats.',
      },
    },
  },
  argTypes: {
    use12Hour: { control: 'boolean' },
    disabled: { control: 'boolean' },
    minuteStep: { control: 'number' },
  },
} satisfies Meta<typeof TimePicker>;

export default meta;
type Story = StoryObj<typeof meta>;

function TimeHost(props: { use12Hour?: boolean; minuteStep?: number; min?: string; max?: string }) {
  const [value, setValue] = useState('');
  return (
    <div className="w-64 space-y-2">
      <TimePicker
        value={value}
        onChange={setValue}
        use12Hour={props.use12Hour}
        minuteStep={props.minuteStep}
        min={props.min}
        max={props.max}
      />
      <p className="text-sm text-muted-foreground">
        Selected: <code className="font-mono">{value || '—'}</code>
      </p>
    </div>
  );
}

export const Default: Story = {
  render: () => <TimeHost />,
};

export const TwelveHour: Story = {
  render: () => <TimeHost use12Hour />,
};

/**
 * Story bodies live in components, not in `render`.
 *
 * `render` is a plain callback with no identity of its own in React, so hooks
 * called there belong to whatever tree Storybook happens to mount and their
 * state survives or resets in ways nothing here controls. That is what
 * `react-hooks/rules-of-hooks` is flagging.
 */
function WithDefaultValueDemo() {
  const [value, setValue] = useState('14:30');
  return (
    <div className="w-64 space-y-2">
      <TimePicker value={value} onChange={setValue} />
      <p className="text-sm text-muted-foreground">
        Selected: <code className="font-mono">{value}</code>
      </p>
    </div>
  );
}

export const WithDefaultValue: Story = {
  render: () => <WithDefaultValueDemo />,
};

export const MinuteStep: Story = {
  render: () => <TimeHost minuteStep={15} />,
};

export const WithRange: Story = {
  render: () => <TimeHost min="09:00" max="17:00" />,
};
