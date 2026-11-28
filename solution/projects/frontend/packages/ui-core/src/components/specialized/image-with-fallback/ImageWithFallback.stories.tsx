import type { Meta, StoryObj } from '@storybook/react-vite';
import { ImageWithFallback, Skeleton } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Specialized/ImageWithFallback',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Image with built-in loading state, error fallback, and customizable fallback icons or content.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

const WORKING_SRC =
  'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400';
const BROKEN_SRC = 'https://this-domain-does-not-exist.example.invalid/x.jpg';

export const Default: Story = {
  render: () => (
    <ImageWithFallback
      src={WORKING_SRC}
      alt="Sample car"
      className="h-48 w-72 rounded-lg"
    />
  ),
};

export const BrokenSrc: Story = {
  render: () => (
    <ImageWithFallback
      src={BROKEN_SRC}
      alt="Broken image"
      fallbackIcon="car"
      className="h-48 w-72 rounded-lg"
    />
  ),
};

export const WithSkeletonFallback: Story = {
  render: () => (
    <ImageWithFallback
      src={BROKEN_SRC}
      alt="Skeleton fallback"
      fallbackContent={<Skeleton className="h-48 w-72 rounded-lg" />}
      className="h-48 w-72 rounded-lg"
    />
  ),
};

export const Square: Story = {
  render: () => (
    <div className="flex items-end gap-4">
      <ImageWithFallback
        src={WORKING_SRC}
        alt="Square"
        className="h-32 w-32 rounded-md"
      />
      <ImageWithFallback
        src=""
        alt="Square fallback"
        fallbackIcon="image"
        className="h-32 w-32 rounded-md"
      />
      <ImageWithFallback
        src=""
        alt="Avatar fallback"
        fallbackIcon="user"
        className="h-32 w-32 rounded-full"
      />
    </div>
  ),
};

export const FallbackIcons: Story = {
  render: () => (
    <div className="grid grid-cols-5 gap-3">
      {(['car', 'image', 'user', 'package', 'location'] as const).map((icon) => (
        <div key={icon} className="flex flex-col items-center gap-2">
          <ImageWithFallback
            src=""
            alt={icon}
            fallbackIcon={icon}
            className="h-20 w-20 rounded-md"
          />
          <span className="text-muted-foreground text-xs">{icon}</span>
        </div>
      ))}
    </div>
  ),
};
