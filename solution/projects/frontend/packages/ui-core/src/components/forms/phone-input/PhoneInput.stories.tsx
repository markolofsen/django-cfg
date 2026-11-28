import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Label, PhoneInput } from '@djangocfg/ui-core/components';
import type { PhoneInputProps } from '@djangocfg/ui-core/components';

const meta: Meta<PhoneInputProps> = {
  title: 'Packages/UI Core/Forms/PhoneInput',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'International phone input backed by `libphonenumber-js`. Includes a built-in country selector with flag, dial code and search.',
      },
    },
  },
  argTypes: {
    defaultCountry: {
      control: { type: 'select' },
      options: ['US', 'GB', 'DE', 'FR', 'JP', 'RU', 'BR', 'IN', 'CN'],
    },
    disabled: { control: 'boolean' },
    placeholder: { control: 'text' },
  },
};

export default meta;

type Story = StoryObj<PhoneInputProps>;

function PhoneHost(args: PhoneInputProps) {
  const [value, setValue] = useState<string | undefined>(args.value);
  return (
    <div className="w-80 space-y-2">
      <Label htmlFor="phone">Phone number</Label>
      <PhoneInput {...args} value={value} onChange={setValue} />
      <p className="text-sm text-muted-foreground">
        Value: <code className="font-mono">{value || '—'}</code>
      </p>
    </div>
  );
}

export const Default: Story = {
  args: { defaultCountry: 'US', placeholder: '(555) 123-4567' },
  render: (args) => <PhoneHost {...args} />,
};

export const WithCountrySelector: Story = {
  args: { defaultCountry: 'DE', placeholder: 'Enter phone' },
  render: (args) => <PhoneHost {...args} />,
};

export const PreFilled: Story = {
  args: { defaultCountry: 'US', value: '+14155552671' },
  render: (args) => <PhoneHost {...args} />,
};

export const Disabled: Story = {
  args: { defaultCountry: 'US', value: '+14155552671', disabled: true },
  render: (args) => <PhoneHost {...args} />,
};
