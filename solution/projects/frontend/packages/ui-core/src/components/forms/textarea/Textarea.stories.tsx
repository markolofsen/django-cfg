import type { Meta, StoryObj } from '@storybook/react-vite';
import { Textarea, Label } from '@djangocfg/ui-core/components';

const meta: Meta<typeof Textarea> = {
  title: 'Packages/UI Core/Forms/Textarea',
  component: Textarea,
  tags: ['autodocs'],
  args: { placeholder: 'Type a message…', rows: 4 },
};

export default meta;

type Story = StoryObj<typeof Textarea>;

export const Default: Story = {
  render: (args) => (
    <div className="grid w-80 gap-1.5">
      <Label htmlFor="msg">Message</Label>
      <Textarea id="msg" {...args} />
    </div>
  ),
};

export const Disabled: Story = {
  args: { disabled: true, defaultValue: 'Read-only content.' },
  render: Default.render!,
};

export const WithDefaultValue: Story = {
  args: { defaultValue: 'This is some default text that was pre-filled.' },
  render: Default.render!,
};

export const Sizes: Story = {
  render: () => (
    <div className="grid w-80 gap-4">
      <div className="grid gap-1.5">
        <Label>Small (2 rows)</Label>
        <Textarea placeholder="Small" rows={2} />
      </div>
      <div className="grid gap-1.5">
        <Label>Medium (4 rows)</Label>
        <Textarea placeholder="Medium" rows={4} />
      </div>
      <div className="grid gap-1.5">
        <Label>Large (8 rows)</Label>
        <Textarea placeholder="Large" rows={8} />
      </div>
    </div>
  ),
};

export const WithCharacterCount: Story = {
  render: () => (
    <div className="grid w-80 gap-1.5">
      <Label htmlFor="limited">Description</Label>
      <Textarea id="limited" placeholder="Enter description…" maxLength={200} />
      <p className="text-right text-sm text-muted-foreground">0/200</p>
    </div>
  ),
};
