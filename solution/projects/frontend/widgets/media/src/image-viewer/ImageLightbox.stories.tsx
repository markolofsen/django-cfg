import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';

import { LazyImageLightbox } from '.';
import type { LightboxImage } from '.';

/**
 * ImageLightbox — the modal gallery a click on a picture opens.
 *
 * What to verify here:
 * - Double-click zooms in at the pointer and the next double-click zooms back
 *   OUT to fit; the cursor is a magnifier at rest and a hand only while zoomed.
 * - Wheel / pinch zoom, drag to pan when zoomed, swipe or arrows to move,
 *   Esc / backdrop click / pull-down to close, thumbnails jump to a slide.
 * - The skin follows the theme and the preset toolbar: switch light/dark and
 *   `Preset` and the backdrop, icons and thumbnail ring follow the tokens.
 */

const SAMPLES: LightboxImage[] = [
  { name: 'mountains.jpg', src: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=2000' },
  { name: 'forest.jpg', src: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=2000' },
  { name: 'lake.jpg', src: 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=2000' },
  { name: 'city.jpg', src: 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=2000' },
];

function Grid({ images, thumbnails }: { images: LightboxImage[]; thumbnails?: boolean }) {
  const [index, setIndex] = useState<number | null>(null);
  return (
    <div className="p-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {images.map((image, i) => (
          <button
            key={image.src}
            type="button"
            onClick={() => setIndex(i)}
            className="overflow-hidden rounded-lg border border-border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <img src={image.src.replace('w=2000', 'w=400')} alt={image.name} className="aspect-4/3 w-full object-cover" />
          </button>
        ))}
      </div>
      <LazyImageLightbox
        images={images}
        open={index !== null}
        index={index ?? 0}
        onIndexChange={setIndex}
        onClose={() => setIndex(null)}
        thumbnails={thumbnails}
      />
    </div>
  );
}

const meta = {
  title: 'Widgets/Media/ImageLightbox',
  component: Grid,
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof Grid>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Gallery: Story = { args: { images: SAMPLES } };

export const SingleImage: Story = { args: { images: SAMPLES.slice(0, 1) } };

export const NoThumbnails: Story = { args: { images: SAMPLES, thumbnails: false } };
