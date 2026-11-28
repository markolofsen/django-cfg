import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Checkbox, Label } from '@djangocfg/ui-core/components';

const meta: Meta<typeof Checkbox> = {
  title: 'Packages/UI Core/Forms/Checkbox',
  component: Checkbox,
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof Checkbox>;

export const Default: Story = {
  render: (args) => (
    <div className="flex items-center gap-2">
      <Checkbox id="terms" {...args} />
      <Label htmlFor="terms">Accept terms and conditions</Label>
    </div>
  ),
};

export const Checked: Story = {
  args: { defaultChecked: true },
  render: Default.render!,
};

export const Disabled: Story = {
  args: { disabled: true, defaultChecked: true },
  render: Default.render!,
};

function CheckboxForm() {
  const [items, setItems] = useState({
    notifications: true,
    marketing: false,
    updates: true,
  });
  return (
    <div className="space-y-4">
      {(['notifications', 'marketing', 'updates'] as const).map((k) => (
        <div key={k} className="flex items-center space-x-2">
          <Checkbox
            id={k}
            checked={items[k]}
            onCheckedChange={(c) => setItems({ ...items, [k]: !!c })}
          />
          <Label htmlFor={k} className="capitalize">
            Receive {k}
          </Label>
        </div>
      ))}
    </div>
  );
}

export const WithForm: Story = {
  render: () => <CheckboxForm />,
};
