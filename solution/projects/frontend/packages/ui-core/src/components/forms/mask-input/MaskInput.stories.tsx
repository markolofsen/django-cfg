import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { MaskInput } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/MaskInput',
  component: MaskInput,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'An input component with configurable mask pattern support for formatted data entry.',
      },
    },
  },
  argTypes: {
    mask: { control: 'text' },
    maskChar: { control: 'text' },
    alwaysShowMask: { control: 'boolean' },
    cleanOnBlur: { control: 'boolean' },
  },
  args: {
    mask: '',
  },
} satisfies Meta<typeof MaskInput>;

export default meta;
type Story = StoryObj<typeof meta>;

function MaskHost(props: { mask: string; placeholder?: string; maskChar?: string; alwaysShowMask?: boolean; cleanOnBlur?: boolean }) {
  const [value, setValue] = useState('');
  return (
    <div className="w-80 space-y-2">
      <MaskInput
        mask={props.mask}
        value={value}
        onChange={setValue}
        placeholder={props.placeholder}
        maskChar={props.maskChar}
        alwaysShowMask={props.alwaysShowMask}
        cleanOnBlur={props.cleanOnBlur}
      />
      <p className="text-sm text-muted-foreground">
        Raw: <code className="font-mono">{value || '—'}</code>
      </p>
    </div>
  );
}

export const Phone: Story = {
  render: () => <MaskHost mask="(000) 000-0000" placeholder="(555) 123-4567" />,
};

export const Date: Story = {
  render: () => <MaskHost mask="00/00/0000" placeholder="MM/DD/YYYY" />,
};

export const CreditCard: Story = {
  render: () => <MaskHost mask="0000 0000 0000 0000" placeholder="1234 5678 9012 3456" />,
};

export const SSN: Story = {
  render: () => <MaskHost mask="000-00-0000" placeholder="123-45-6789" />,
};

export const CustomMaskChar: Story = {
  render: () => <MaskHost mask="(000) 000-0000" maskChar="#" alwaysShowMask />,
};

export const CleanOnBlur: Story = {
  render: () => <MaskHost mask="(000) 000-0000" cleanOnBlur />,
};
