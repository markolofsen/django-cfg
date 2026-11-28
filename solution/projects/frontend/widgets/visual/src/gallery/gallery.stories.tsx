import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Gallery,
  GalleryCompact,
  GalleryGrid,
  type GalleryMediaItem,
} from '.';

const CAT: GalleryMediaItem = { id: '1', src: 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=900', alt: 'Cat' };
const DOG: GalleryMediaItem = { id: '2', src: 'https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=900', alt: 'Dog' };
const BIRDS: GalleryMediaItem = { id: '3', src: 'https://images.unsplash.com/photo-1444464666168-49d633b86797?w=900', alt: 'Birds' };
const MOUNTAINS: GalleryMediaItem = { id: '4', src: 'https://images.unsplash.com/photo-1551279880-03041531948f?w=900', alt: 'Mountains' };
const FOREST: GalleryMediaItem = { id: '5', src: 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=900', alt: 'Forest' };
const FIELD: GalleryMediaItem = { id: '6', src: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900', alt: 'Field' };

const IMAGES: GalleryMediaItem[] = [CAT, DOG, BIRDS, MOUNTAINS, FOREST, FIELD];

const MIXED: GalleryMediaItem[] = [
  CAT,
  {
    id: 'v1',
    type: 'video',
    src: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=900',
    videoSrc:
      'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    videoType: 'video/mp4',
    alt: 'Big Buck Bunny',
  },
  DOG,
  BIRDS,
  {
    id: 'v2',
    type: 'video',
    src: 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=900',
    videoSrc:
      'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
    videoType: 'video/mp4',
    alt: 'Elephants Dream',
  },
  MOUNTAINS,
];

const meta = {
  title: 'Widgets/Visual/Gallery',
  component: GalleryCompact,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Gallery surface kit: `GalleryCompact` (card carousel), `GalleryGrid` (Airbnb-style mosaic), and `Gallery` (orchestrator with thumbnails + lightbox). Mix images and videos via `type: "video"` on items.',
      },
    },
  },
  args: { images: IMAGES },
} satisfies Meta<typeof GalleryCompact>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * Playground for `GalleryCompact` — tune the carousel surface used inside cards.
 */
export const Playground: Story = {
  args: {
    aspectRatio: '16/9',
    showDots: true,
    showArrows: true,
    showCounter: true,
    enableZoom: true,
    maxDots: 5,
  },
  argTypes: {
    aspectRatio: {
      control: 'inline-radio',
      options: ['16/9', '4/3', '3/2', '1/1', 'auto'],
      table: { category: 'Layout' },
    },
    showDots: { control: 'boolean', table: { category: 'Chrome' } },
    showArrows: { control: 'boolean', table: { category: 'Chrome' } },
    showCounter: { control: 'boolean', table: { category: 'Chrome' } },
    enableZoom: { control: 'boolean', table: { category: 'Behaviour' } },
    maxDots: {
      control: { type: 'number', min: 1, max: 10, step: 1 },
      table: { category: 'Chrome' },
    },
  },
  render: (args) => (
    <div className="w-[640px]">
      <GalleryCompact {...args} />
    </div>
  ),
};

/**
 * Compact carousel inside a typical product card — the most common deployment.
 */
export const CompactCarousel: Story = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-[720px]">
      {[0, 1].map((i) => (
        <div key={i} className="rounded-xl border border-border overflow-hidden bg-card">
          <GalleryCompact
            images={IMAGES}
            aspectRatio="4/3"
            showDots
            showCounter
            maxDots={5}
          />
          <div className="p-4">
            <h3 className="font-medium text-sm">Listing {i + 1}</h3>
            <p className="text-xs text-muted-foreground">$24,900 · 12k miles</p>
          </div>
        </div>
      ))}
    </div>
  ),
};

/**
 * Airbnb-style grid mosaic — layout auto-picks from image count, but you can pin one.
 */
export const GridMasonry: Story = {
  render: () => (
    <div className="space-y-8 w-[820px]">
      <div>
        <div className="text-xs font-medium text-muted-foreground mb-2">{'layout="mosaic-5"'}</div>
        <GalleryGrid images={IMAGES} layout="mosaic-5" rounded="lg" gap={2} showMoreBadge />
      </div>
      <div>
        <div className="text-xs font-medium text-muted-foreground mb-2">{'layout="hero-left"'}</div>
        <GalleryGrid images={IMAGES.slice(0, 3)} layout="hero-left" rounded="lg" gap={2} />
      </div>
      <div>
        <div className="text-xs font-medium text-muted-foreground mb-2">{'layout="grid-2x2"'}</div>
        <GalleryGrid images={IMAGES.slice(0, 4)} layout="grid-2x2" rounded="lg" gap={2} />
      </div>
    </div>
  ),
};

/**
 * Full `Gallery` orchestrator — main image, thumbnail strip, click to open lightbox.
 */
export const Lightbox: Story = {
  render: () => (
    <div className="w-[820px]">
      <Gallery
        images={IMAGES}
        previewMode="carousel"
        showThumbnails
        showControls
        showCounter
        enableLightbox
        enableKeyboard
        aspectRatio={16 / 9}
      />
    </div>
  ),
};

/**
 * Mixed media — `type: "video"` items render inline video players inside the gallery.
 */
export const MixedMedia: Story = {
  render: () => (
    <div className="w-[820px]">
      <Gallery
        images={MIXED}
        previewMode="carousel"
        showThumbnails
        showControls
        showCounter
        enableLightbox
        enableKeyboard
        aspectRatio={16 / 9}
      />
    </div>
  ),
};
