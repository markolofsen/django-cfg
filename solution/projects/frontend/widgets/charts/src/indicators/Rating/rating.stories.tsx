import { useState, type ReactNode } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Star } from 'lucide-react';
import { Rating, RatingItem } from '.';

type Step = 0.5 | 1;

const meta = {
  title: 'Widgets/Charts/Rating',
  component: Rating,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'An accessible rating component with keyboard navigation and partial values.',
      },
    },
  },
  argTypes: {
    max: { control: 'number' },
    step: { control: 'number' },
    size: { control: 'select', options: ['sm', 'default', 'lg'] },
    clearable: { control: 'boolean' },
    disabled: { control: 'boolean' },
    readOnly: { control: 'boolean' },
  },
} satisfies Meta<typeof Rating>;

export default meta;
type Story = StoryObj<typeof meta>;

function RatingHost(props: {
  defaultValue?: number;
  max?: number;
  step?: Step;
  size?: 'sm' | 'default' | 'lg';
  clearable?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  icon?: ReactNode;
}) {
  const [value, setValue] = useState(props.defaultValue ?? 0);
  return (
    <div className="space-y-2">
      <Rating
        value={value}
        onValueChange={setValue}
        max={props.max}
        step={props.step}
        size={props.size}
        clearable={props.clearable}
        disabled={props.disabled}
        readOnly={props.readOnly}
      >
        {Array.from({ length: props.max ?? 5 }).map((_, i) => (
          <RatingItem key={i} index={i}>
            {props.icon}
          </RatingItem>
        ))}
      </Rating>
      <p className="text-sm text-muted-foreground">
        Value: <code className="font-mono">{value}</code>
      </p>
    </div>
  );
}

export const Default: Story = {
  render: () => <RatingHost defaultValue={3} />,
};

export const Empty: Story = {
  render: () => <RatingHost />,
};

export const HalfSteps: Story = {
  render: () => <RatingHost defaultValue={3.5} step={0.5} />,
};

export const Large: Story = {
  render: () => <RatingHost defaultValue={4} size="lg" />,
};

export const Small: Story = {
  render: () => <RatingHost defaultValue={2} size="sm" />,
};

export const Clearable: Story = {
  render: () => <RatingHost defaultValue={4} clearable />,
};

export const Disabled: Story = {
  render: () => <RatingHost defaultValue={3} disabled />,
};

export const ReadOnly: Story = {
  render: () => <RatingHost defaultValue={4} readOnly />,
};

export const CustomIcon: Story = {
  render: () => <RatingHost defaultValue={3} icon={<Star className="size-6" />} />,
};
