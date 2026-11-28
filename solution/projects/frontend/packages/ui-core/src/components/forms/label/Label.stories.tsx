import type { Meta, StoryObj } from '@storybook/react-vite';
import { Input, Label } from '@djangocfg/ui-core/components';

const meta: Meta<typeof Label> = {
  title: 'Packages/UI Core/Forms/Label',
  component: Label,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Accessible label primitive built on Radix UI. Use `htmlFor` to associate with a form control.',
      },
    },
  },
};

export default meta;

type Story = StoryObj<typeof Label>;

export const Default: Story = {
  render: () => (
    <div className="w-72 space-y-2">
      <Label htmlFor="email">Email</Label>
      <Input id="email" type="email" placeholder="you@example.com" />
    </div>
  ),
};

export const WithRequired: Story = {
  render: () => (
    <div className="w-72 space-y-2">
      <Label htmlFor="name">
        Full name <span className="text-destructive">*</span>
      </Label>
      <Input id="name" placeholder="Ada Lovelace" required />
    </div>
  ),
};

export const WithDescription: Story = {
  render: () => (
    <div className="w-72 space-y-1.5">
      <Label htmlFor="bio">Bio</Label>
      <p className="text-sm text-muted-foreground">
        Tell us a little about yourself. Markdown is supported.
      </p>
      <Input id="bio" placeholder="I am..." />
    </div>
  ),
};
