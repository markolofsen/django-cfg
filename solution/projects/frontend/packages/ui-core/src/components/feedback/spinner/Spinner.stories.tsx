import type { Meta, StoryObj } from '@storybook/react-vite';
import { Spinner } from '@djangocfg/ui-core/components';

const meta: Meta<typeof Spinner> = {
  title: 'Packages/UI Core/Feedback/Spinner',
  component: Spinner,
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof Spinner>;

export const Default: Story = {};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Spinner className="h-3 w-3" />
      <Spinner className="h-5 w-5" />
      <Spinner className="h-8 w-8" />
      <Spinner className="h-12 w-12" />
    </div>
  ),
};

export const InButton: Story = {
  render: () => (
    <button className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-primary-foreground">
      <Spinner className="h-4 w-4" />
      Loading…
    </button>
  ),
};

export const Centered: Story = {
  render: () => (
    <div className="flex h-40 w-80 items-center justify-center rounded-lg border">
      <Spinner className="h-8 w-8" />
    </div>
  ),
};

export const WithText: Story = {
  render: () => (
    <div className="flex flex-col items-center gap-2">
      <Spinner className="h-8 w-8" />
      <span className="text-sm text-muted-foreground">Loading data…</span>
    </div>
  ),
};
