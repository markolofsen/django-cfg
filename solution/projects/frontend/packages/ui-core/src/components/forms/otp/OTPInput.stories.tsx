import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { OTPInput } from '@djangocfg/ui-core/components';
import type {
  OTPInputProps,
  OTPPasteBehavior,
  OTPValidationMode,
} from '@djangocfg/ui-core/components';

const meta: Meta<OTPInputProps> = {
  title: 'Packages/UI Core/Forms/OTPInput',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Smart OTP component with validation modes, paste behaviour and auto-submit. Uses `useSmartOTP` internally.',
      },
    },
  },
  argTypes: {
    length: { control: { type: 'number', min: 4, max: 8, step: 1 } },
    validationMode: {
      control: { type: 'select' },
      options: ['numeric', 'alphanumeric', 'alpha', 'custom'] satisfies OTPValidationMode[],
    },
    pasteBehavior: {
      control: { type: 'select' },
      options: ['clean', 'strict', 'lenient'] satisfies OTPPasteBehavior[],
    },
    autoSubmit: { control: 'boolean' },
    disabled: { control: 'boolean' },
    showSeparator: { control: 'boolean' },
    error: { control: 'boolean' },
    success: { control: 'boolean' },
    size: {
      control: { type: 'inline-radio' },
      options: ['sm', 'default', 'lg'],
    },
  },
};

export default meta;

type Story = StoryObj<OTPInputProps>;

function PlaygroundHost(args: OTPInputProps) {
  const [value, setValue] = useState('');
  return (
    <div className="space-y-3">
      <OTPInput {...args} value={value} onChange={setValue} />
      <p className="text-sm text-muted-foreground">
        Value: <code className="font-mono">{value || '—'}</code>
      </p>
    </div>
  );
}

export const Playground: Story = {
  args: {
    length: 6,
    validationMode: 'numeric',
    pasteBehavior: 'clean',
    autoSubmit: false,
    disabled: false,
    showSeparator: false,
    error: false,
    success: false,
  },
  render: (args) => <PlaygroundHost {...args} />,
};

export const Numeric: Story = {
  args: { length: 6, validationMode: 'numeric' },
  render: (args) => <PlaygroundHost {...args} />,
};

export const Alphanumeric: Story = {
  args: { length: 6, validationMode: 'alphanumeric' },
  render: (args) => <PlaygroundHost {...args} />,
};

function ValidatorHost() {
  const [value, setValue] = useState('');
  // Accept only even-numeric digits
  const isEvenDigit = (v: string) => /^[02468]*$/.test(v);
  return (
    <div className="space-y-3">
      <OTPInput
        length={6}
        validationMode="custom"
        customValidator={isEvenDigit}
        value={value}
        onChange={setValue}
      />
      <p className="text-sm text-muted-foreground">
        Only even digits (0, 2, 4, 6, 8) are accepted.
      </p>
    </div>
  );
}

export const WithValidator: Story = {
  render: () => <ValidatorHost />,
};
