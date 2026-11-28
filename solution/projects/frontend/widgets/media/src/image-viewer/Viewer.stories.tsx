import type { Meta, StoryObj } from '@storybook/react-vite';
import { LazyImageViewer as ImageViewer } from '.';

const SAMPLES = [
  {
    file: { name: 'mountains.jpg', path: 'mountains' },
    src: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600',
  },
  {
    file: { name: 'forest.jpg', path: 'forest' },
    src: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1600',
  },
  {
    file: { name: 'lake.jpg', path: 'lake' },
    src: 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=1600',
  },
  {
    file: { name: 'city.jpg', path: 'city' },
    src: 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=1600',
  },
  {
    file: { name: 'wildlife.jpg', path: 'wildlife' },
    src: 'https://images.unsplash.com/photo-1444464666168-49d633b86797?w=1600',
  },
];

const LARGE_SAMPLES = SAMPLES.map((s) => ({
  ...s,
  src: s.src.replace('w=1600', 'w=3200'),
}));

const meta = {
  title: 'Widgets/Media/Viewer',
  component: ImageViewer,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Image viewer with wheel-zoom, pan, rotation, flip, and gallery navigation. Pass either `src` (URL) or `content` (ArrayBuffer/base64) per item. Toolbar and info are always rendered by the component; `inDialog` hides the expand button when already mounted inside a dialog.',
      },
    },
  },
  argTypes: {
    initialIndex: {
      control: { type: 'number', min: 0, max: 4, step: 1 },
      description: 'Index of the image to open first.',
      table: { category: 'Gallery' },
    },
    inDialog: {
      control: 'boolean',
      description: 'Hide the expand-to-fullscreen button (use when already inside a dialog).',
      table: { category: 'Chrome' },
    },
  },
} satisfies Meta<typeof ImageViewer>;

export default meta;

type Story = StoryObj<typeof meta>;

const renderFrame: Story['render'] = (args) => (
  <div className="h-[500px] w-[720px]">
    <ImageViewer {...args} />
  </div>
);

export const Playground: Story = {
  args: {
    images: SAMPLES,
    initialIndex: 0,
    inDialog: false,
  },
  render: renderFrame,
};

export const Single: Story = {
  args: { images: SAMPLES.slice(0, 1) },
  render: renderFrame,
};

export const Gallery: Story = {
  args: { images: SAMPLES, initialIndex: 0 },
  render: renderFrame,
};

export const GalleryMode: Story = Gallery;

export const WithToolbar: Story = {
  args: { images: SAMPLES.slice(0, 3), initialIndex: 1 },
  render: renderFrame,
  parameters: {
    docs: {
      description: {
        story:
          'Default chrome: zoom presets, rotate, flip H/V, and gallery prev/next are rendered above the canvas.',
      },
    },
  },
};

export const WithInfo: Story = {
  args: { images: SAMPLES.slice(0, 2), initialIndex: 0 },
  render: renderFrame,
  parameters: {
    docs: {
      description: {
        story:
          'ImageInfo (filename + intrinsic dimensions) is rendered by the viewer once the image resolves.',
      },
    },
  },
};

export const NoChrome: Story = {
  args: { images: SAMPLES.slice(0, 1), inDialog: true },
  render: renderFrame,
  parameters: {
    docs: {
      description: {
        story:
          '`inDialog` removes the expand button — use this when the viewer is already mounted inside a fullscreen dialog.',
      },
    },
  },
};

export const LargeImages: Story = {
  args: { images: LARGE_SAMPLES, initialIndex: 0 },
  render: renderFrame,
  parameters: {
    docs: {
      description: {
        story:
          'Higher-resolution sources (w=3200) exercise progressive loading and the LQIP placeholder path.',
      },
    },
  },
};
