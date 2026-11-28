import type { Meta, StoryObj } from '@storybook/react-vite';
import { Badge } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Badge',
  component: Badge,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'destructive', 'outline'],
    },
  },
  args: { children: 'Badge' },
} satisfies Meta<typeof Badge>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Variants: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <Badge>Default</Badge>
      <Badge variant="secondary">Secondary</Badge>
      <Badge variant="destructive">Destructive</Badge>
      <Badge variant="outline">Outline</Badge>
    </div>
  ),
};

export const StatusBadges: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge>Active</Badge>
      <Badge variant="secondary">Pending</Badge>
      <Badge variant="destructive">Expired</Badge>
      <Badge variant="outline">Draft</Badge>
    </div>
  ),
};

export const InContext: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="font-medium">Status:</span>
        <Badge>Published</Badge>
      </div>
      <div className="flex items-center gap-2">
        <span className="font-medium">Tags:</span>
        <Badge variant="secondary">React</Badge>
        <Badge variant="secondary">TypeScript</Badge>
        <Badge variant="secondary">UI</Badge>
      </div>
    </div>
  ),
};
