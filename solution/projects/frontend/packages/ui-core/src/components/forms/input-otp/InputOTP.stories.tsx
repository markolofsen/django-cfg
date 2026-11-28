import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from '@djangocfg/ui-core/components';

const meta: Meta<typeof InputOTP> = {
  title: 'Packages/UI Core/Forms/InputOTP',
  component: InputOTP,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Low-level OTP input with individual slot rendering. For high-level UX (paste behavior, validation modes, presets) prefer `OTPInput`.',
      },
    },
  },
};

export default meta;

type Story = StoryObj<typeof InputOTP>;

function ControlledSix() {
  const [value, setValue] = useState('');
  return (
    <InputOTP maxLength={6} value={value} onChange={setValue}>
      <InputOTPGroup>
        <InputOTPSlot index={0} />
        <InputOTPSlot index={1} />
        <InputOTPSlot index={2} />
        <InputOTPSlot index={3} />
        <InputOTPSlot index={4} />
        <InputOTPSlot index={5} />
      </InputOTPGroup>
    </InputOTP>
  );
}

export const Default: Story = {
  render: () => <ControlledSix />,
};

function ControlledWithSeparator() {
  const [value, setValue] = useState('');
  return (
    <InputOTP maxLength={6} value={value} onChange={setValue}>
      <InputOTPGroup>
        <InputOTPSlot index={0} />
        <InputOTPSlot index={1} />
        <InputOTPSlot index={2} />
      </InputOTPGroup>
      <InputOTPSeparator />
      <InputOTPGroup>
        <InputOTPSlot index={3} />
        <InputOTPSlot index={4} />
        <InputOTPSlot index={5} />
      </InputOTPGroup>
    </InputOTP>
  );
}

export const WithSeparator: Story = {
  render: () => <ControlledWithSeparator />,
};

export const Disabled: Story = {
  render: () => (
    <InputOTP maxLength={6} disabled>
      <InputOTPGroup>
        <InputOTPSlot index={0} />
        <InputOTPSlot index={1} />
        <InputOTPSlot index={2} />
        <InputOTPSlot index={3} />
        <InputOTPSlot index={4} />
        <InputOTPSlot index={5} />
      </InputOTPGroup>
    </InputOTP>
  ),
};

function CompactFour() {
  const [value, setValue] = useState('');
  return (
    <InputOTP maxLength={4} value={value} onChange={setValue}>
      <InputOTPGroup>
        <InputOTPSlot index={0} />
        <InputOTPSlot index={1} />
        <InputOTPSlot index={2} />
        <InputOTPSlot index={3} />
      </InputOTPGroup>
    </InputOTP>
  );
}

export const Compact: Story = {
  render: () => <CompactFour />,
};
