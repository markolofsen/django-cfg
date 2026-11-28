import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Preloader,
  PreloaderSkeleton,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Feedback/Preloader',
  component: Preloader,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Universal loading indicator with size variants and an optional skeleton companion (`PreloaderSkeleton`) for content placeholders.',
      },
    },
  },
  argTypes: {
    size: { control: 'select', options: ['sm', 'md', 'lg', 'xl'] },
    variant: { control: 'select', options: ['inline', 'fullscreen'] },
    text: { control: 'text' },
    description: { control: 'text' },
    backdrop: { control: 'boolean' },
    backdropOpacity: { control: { type: 'number', min: 0, max: 100, step: 10 } },
  },
} satisfies Meta<typeof Preloader>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { size: 'md' },
};

export const Compact: Story = {
  render: () => (
    <div className="flex items-center gap-8">
      <div className="flex flex-col items-center gap-2">
        <Preloader size="sm" />
        <span className="text-xs text-muted-foreground">sm</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Preloader size="md" />
        <span className="text-xs text-muted-foreground">md</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Preloader size="lg" />
        <span className="text-xs text-muted-foreground">lg</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Preloader size="xl" />
        <span className="text-xs text-muted-foreground">xl</span>
      </div>
    </div>
  ),
};

export const WithText: Story = {
  render: () => (
    <div className="flex flex-col gap-6">
      <Preloader text="Loading data..." />
      <Preloader
        size="lg"
        text="Processing"
        description="Please wait while we process your request"
      />
      <div className="rounded-lg border p-8">
        <Preloader text="Loading content..." size="lg" />
      </div>
    </div>
  ),
};

export const Custom: Story = {
  render: () => (
    <div className="flex flex-col gap-8 max-w-md">
      <div>
        <p className="text-xs text-muted-foreground mb-2">Default skeleton</p>
        <PreloaderSkeleton />
      </div>
      <div>
        <p className="text-xs text-muted-foreground mb-2">With avatar</p>
        <PreloaderSkeleton showAvatar />
      </div>
      <div>
        <p className="text-xs text-muted-foreground mb-2">Custom line counts</p>
        <div className="space-y-6">
          <PreloaderSkeleton lines={2} />
          <PreloaderSkeleton lines={4} />
          <PreloaderSkeleton lines={1} />
        </div>
      </div>
      <div className="rounded-lg border p-4">
        <PreloaderSkeleton showAvatar lines={2} />
      </div>
    </div>
  ),
};
