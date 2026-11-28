import type { Meta, StoryObj } from '@storybook/react-vite';
import { AspectRatio } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Layout/AspectRatio',
  component: AspectRatio,
  tags: ['autodocs'],
} satisfies Meta<typeof AspectRatio>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Sixteen9: Story = {
  render: () => (
    <div className="w-[480px]">
      <AspectRatio ratio={16 / 9} className="overflow-hidden rounded-md bg-muted">
        <img
          src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900"
          alt="field"
          className="h-full w-full object-cover"
        />
      </AspectRatio>
    </div>
  ),
};

export const FourThree: Story = {
  render: () => (
    <div className="w-80">
      <AspectRatio ratio={4 / 3} className="overflow-hidden rounded-md bg-muted">
        <img
          src="https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=600"
          alt="porsche"
          className="h-full w-full object-cover"
        />
      </AspectRatio>
    </div>
  ),
};

export const WithPlaceholder: Story = {
  render: () => (
    <div className="w-[480px]">
      <AspectRatio
        ratio={16 / 9}
        className="flex items-center justify-center rounded-md bg-muted"
      >
        <span className="text-muted-foreground">No image available</span>
      </AspectRatio>
    </div>
  ),
};

export const Video: Story = {
  render: () => (
    <div className="w-[560px]">
      <AspectRatio ratio={16 / 9} className="overflow-hidden rounded-md bg-black">
        <iframe
          src="https://www.youtube.com/embed/dQw4w9WgXcQ"
          title="Video"
          className="h-full w-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </AspectRatio>
    </div>
  ),
};

export const Square: Story = {
  render: () => (
    <div className="w-64">
      <AspectRatio ratio={1} className="overflow-hidden rounded-md bg-muted">
        <img
          src="https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=600"
          alt="cat"
          className="h-full w-full object-cover"
        />
      </AspectRatio>
    </div>
  ),
};
