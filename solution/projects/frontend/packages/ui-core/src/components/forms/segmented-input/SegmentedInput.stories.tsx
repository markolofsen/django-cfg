import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { SegmentedInput } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/SegmentedInput',
  component: SegmentedInput,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A segmented input for OTPs, codes, and other fixed-length character sequences.',
      },
    },
  },
  argTypes: {
    length: { control: 'number' },
    size: { control: 'select', options: ['sm', 'default', 'lg'] },
    fluid: { control: 'boolean' },
    disabled: { control: 'boolean' },
  },
} satisfies Meta<typeof SegmentedInput>;

export default meta;
type Story = StoryObj<typeof meta>;

function SegmentedHost(props: { length?: number; size?: 'sm' | 'default' | 'lg'; fluid?: boolean; separator?: React.ReactNode; separatorIndices?: number[] }) {
  const [value, setValue] = useState('');
  return (
    <div className="space-y-2">
      <SegmentedInput
        length={props.length}
        size={props.size}
        fluid={props.fluid}
        separator={props.separator}
        separatorIndices={props.separatorIndices}
        value={value}
        onChange={setValue}
      />
      <p className="text-sm text-muted-foreground">
        Value: <code className="font-mono">{value || '—'}</code>
      </p>
    </div>
  );
}

export const Default: Story = {
  render: () => <SegmentedHost length={6} />,
};

export const Sizes: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <SegmentedHost length={4} size="sm" />
      <SegmentedHost length={4} size="default" />
      <SegmentedHost length={4} size="lg" />
    </div>
  ),
};

export const WithSeparator: Story = {
  render: () => <SegmentedHost length={6} separator="-" separatorIndices={[2]} />,
};

export const Fluid: Story = {
  render: () => <SegmentedHost length={6} fluid />,
};

export const ShortCode: Story = {
  render: () => <SegmentedHost length={4} />,
};

export const LongCode: Story = {
  render: () => <SegmentedHost length={8} separator="-" separatorIndices={[3]} />,
};
