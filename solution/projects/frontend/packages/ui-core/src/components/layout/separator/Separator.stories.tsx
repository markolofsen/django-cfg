import type { Meta, StoryObj } from '@storybook/react-vite';
import { Separator } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Layout/Separator',
  component: Separator,
  tags: ['autodocs'],
  argTypes: {
    orientation: { control: 'select', options: ['horizontal', 'vertical'] },
  },
  args: { orientation: 'horizontal' },
} satisfies Meta<typeof Separator>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Horizontal: Story = {
  render: () => (
    <div className="w-80">
      <div className="space-y-1">
        <h4 className="text-sm font-medium">@djangocfg/ui-core</h4>
        <p className="text-sm text-muted-foreground">
          An open-source UI component library.
        </p>
      </div>
      <Separator className="my-4" />
      <div className="flex h-5 items-center space-x-4 text-sm">
        <div>Blog</div>
        <Separator orientation="vertical" />
        <div>Docs</div>
        <Separator orientation="vertical" />
        <div>Source</div>
      </div>
    </div>
  ),
};

export const Vertical: Story = {
  render: () => (
    <div className="flex h-5 items-center space-x-4 text-sm">
      <div>Home</div>
      <Separator orientation="vertical" />
      <div>About</div>
      <Separator orientation="vertical" />
      <div>Products</div>
      <Separator orientation="vertical" />
      <div>Contact</div>
    </div>
  ),
};

export const InCard: Story = {
  render: () => (
    <div className="w-80 rounded-lg border p-4">
      <h4 className="font-medium">Card Title</h4>
      <Separator className="my-3" />
      <p className="text-sm text-muted-foreground">
        Some card content below the separator.
      </p>
    </div>
  ),
};

export const WithLabels: Story = {
  render: () => (
    <div className="w-80">
      <div className="flex items-center gap-4">
        <Separator className="flex-1" />
        <span className="text-sm text-muted-foreground">OR</span>
        <Separator className="flex-1" />
      </div>
    </div>
  ),
};
