import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  GalleryThumbnails,
  GalleryThumbnailsVirtual,
  type GalleryMediaItem,
} from '.';

const IMAGES: GalleryMediaItem[] = [
  { id: '1', src: 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=900', alt: 'Cat' },
  { id: '2', src: 'https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=900', alt: 'Dog' },
  { id: '3', src: 'https://images.unsplash.com/photo-1444464666168-49d633b86797?w=900', alt: 'Birds' },
  { id: '4', src: 'https://images.unsplash.com/photo-1551279880-03041531948f?w=900', alt: 'Mountains' },
  { id: '5', src: 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=900', alt: 'Forest' },
  { id: '6', src: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900', alt: 'Field' },
];

// Every index used below is in range; this only satisfies the compiler's
// `noUncheckedIndexedAccess` and is never reached at runtime.
const FALLBACK: GalleryMediaItem = { id: 'fallback', src: '', alt: '' };

// Synthesize a large list for the virtual variant by recycling the 6 fixtures
const MANY: GalleryMediaItem[] = Array.from({ length: 240 }, (_, i) => {
  const base = IMAGES[i % IMAGES.length] ?? FALLBACK;
  return { ...base, id: `${base.id}-${i}`, alt: `${base.alt} #${i + 1}` };
});

const meta = {
  title: 'Widgets/Visual/Gallery Thumbnails',
  component: GalleryThumbnails,
  args: { images: IMAGES, currentIndex: 0, onSelect: () => {}, size: 'md' },
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Standalone thumbnail strips. `GalleryThumbnails` is a flex row sized for short lists; `GalleryThumbnailsVirtual` windowing-renders large lists (hundreds of items) via the internal `useVirtualList` hook.',
      },
    },
  },
} satisfies Meta<typeof GalleryThumbnails>;

export default meta;

type Story = StoryObj<typeof meta>;

function ThumbnailsDemo({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const [index, setIndex] = useState(0);
  const current = IMAGES[index] ?? FALLBACK;
  return (
    <div className="w-[720px] space-y-3">
      <div className="rounded-lg overflow-hidden border border-border aspect-[16/9] bg-muted">
        <img
          src={current.src}
          alt={current.alt ?? ''}
          className="w-full h-full object-cover"
        />
      </div>
      <GalleryThumbnails
        images={IMAGES}
        currentIndex={index}
        onSelect={setIndex}
        size={size}
      />
      <p className="text-xs text-muted-foreground">
        Selected #{index + 1} — {current.alt}
      </p>
    </div>
  );
}

/**
 * Standard thumbnail strip — sized for small-to-medium image counts.
 */
export const Standard: Story = {
  args: { size: 'md' },
  argTypes: {
    size: {
      control: 'inline-radio',
      options: ['sm', 'md', 'lg'],
      table: { category: 'Layout' },
    },
  },
  render: (args) => <ThumbnailsDemo size={args.size} />,
};

function VirtualDemo({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const [index, setIndex] = useState(0);
  const current = MANY[index] ?? FALLBACK;
  return (
    <div className="w-[720px] space-y-3">
      <div className="rounded-lg overflow-hidden border border-border aspect-[16/9] bg-muted">
        <img
          src={current.src}
          alt={current.alt ?? ''}
          className="w-full h-full object-cover"
        />
      </div>
      <GalleryThumbnailsVirtual
        images={MANY}
        currentIndex={index}
        onSelect={setIndex}
        size={size}
      />
      <p className="text-xs text-muted-foreground">
        {MANY.length} thumbnails virtualized — selected #{index + 1}
      </p>
    </div>
  );
}

/**
 * Virtualised variant — drop-in replacement when the image count would otherwise
 * blow the DOM up. Same props as the standard component.
 */
export const Virtualized: Story = {
  args: { size: 'md' },
  argTypes: {
    size: {
      control: 'inline-radio',
      options: ['sm', 'md', 'lg'],
      table: { category: 'Layout' },
    },
  },
  render: (args) => <VirtualDemo size={args.size} />,
};
