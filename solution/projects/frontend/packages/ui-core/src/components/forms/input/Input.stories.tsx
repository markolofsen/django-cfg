import type { Meta, StoryObj } from '@storybook/react-vite';
import { Input, Label } from '@djangocfg/ui-core/components';

const meta: Meta<typeof Input> = {
  title: 'Packages/UI Core/Forms/Input',
  component: Input,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['text', 'email', 'password', 'number', 'search', 'url'],
    },
    inputSize: { control: 'select', options: ['xs', 'sm', 'default', 'lg'] },
    disabled: { control: 'boolean' },
    placeholder: { control: 'text' },
  },
  args: {
    placeholder: 'you@example.com',
    type: 'email',
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithLabel: Story = {
  render: (args) => (
    <div className="grid w-72 gap-1.5">
      <Label htmlFor="email">Email</Label>
      <Input id="email" {...args} />
    </div>
  ),
};

export const States: Story = {
  render: () => (
    <div className="grid w-72 gap-3">
      <div className="grid gap-1.5">
        <Label htmlFor="empty">Empty</Label>
        <Input id="empty" placeholder="Type here…" />
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="filled">Filled</Label>
        <Input id="filled" defaultValue="Mark" />
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="disabled">Disabled</Label>
        <Input id="disabled" disabled placeholder="Can't touch this" />
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="invalid" className="text-destructive">
          Invalid
        </Label>
        <Input
          id="invalid"
          aria-invalid
          defaultValue="not-an-email"
          className="border-destructive"
        />
      </div>
    </div>
  ),
};

export const Types: Story = {
  render: () => (
    <div className="grid w-72 gap-3">
      <Input type="text" placeholder="Text input" />
      <Input type="email" placeholder="Email input" />
      <Input type="password" placeholder="Password input" />
      <Input type="number" placeholder="Number input" />
      <Input type="search" placeholder="Search input" />
    </div>
  ),
};

export const File: Story = {
  render: () => (
    <div className="grid w-72 gap-1.5">
      <Label htmlFor="file">Upload file</Label>
      <Input id="file" type="file" />
    </div>
  ),
};

export const Persisted: Story = {
  tags: ['manual'],
  parameters: {
    djangocfg: { storage: 'preserve' },
    docs: {
      description: {
        story:
          'Pass `storageKey` to persist the value to localStorage. Useful for filters, search bars, settings — anywhere the value should survive a page reload.',
      },
    },
  },
  render: () => (
    <div className="grid w-72 gap-1.5">
      <Label htmlFor="search">Search (persisted)</Label>
      <Input
        id="search"
        type="search"
        placeholder="Try typing — reload survives"
        storageKey="storybook-input-search"
      />
    </div>
  ),
};
