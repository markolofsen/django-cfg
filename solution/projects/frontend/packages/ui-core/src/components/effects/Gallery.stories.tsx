import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Moon, Sun } from 'lucide-react';
import { GlowBackground, Swap, SwapOff, SwapOn } from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Effects/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'The two decorative components in `ui-core`, side by side. They sit at ' +
          'opposite scales: one paints a whole surface behind your content, the other ' +
          'animates a single glyph the user just clicked. Both need a sized container — ' +
          '`GlowBackground` is absolutely positioned and collapses without one.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

/** `Swap` is controlled — it needs an owner for `swapped` to animate at all. */
function SwapHost({ animation }: { animation: 'fade' | 'rotate' | 'flip' | 'scale' }) {
  const [swapped, setSwapped] = useState(false);
  return (
    <div className="flex flex-col items-center gap-1">
      <Swap swapped={swapped} onSwappedChange={setSwapped} animation={animation}>
        <SwapOn>
          {/* eslint-disable-next-line no-restricted-syntax -- the colour IS the
              subject here, not a status: a sun is yellow and a moon is grey.
              A semantic token would retune them with the theme and say the
              wrong thing while doing it. */}
          <Sun className="size-7 text-yellow-500" />
        </SwapOn>
        <SwapOff>
          {/* eslint-disable-next-line no-restricted-syntax -- the colour IS the
              subject here, not a status: a sun is yellow and a moon is grey.
              A semantic token would retune them with the theme and say the
              wrong thing while doing it. */}
          <Moon className="size-7 text-slate-500" />
        </SwapOff>
      </Swap>
      <span className="text-muted-foreground text-xs">{animation}</span>
    </div>
  );
}

function GlowDemo({ className, label }: { className?: string; label: string }) {
  return (
    <div className="relative h-40 w-full overflow-hidden rounded-md border">
      <GlowBackground className={className} />
      <div className="text-muted-foreground relative z-10 p-3 text-xs">{label}</div>
    </div>
  );
}

/**
 * The whole group on one screen.
 *
 * Split by scale — a page backdrop and a click-sized transition share a folder
 * but are never alternatives to each other.
 */
export const AllEffects: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="Surface-scale backdrop">
        <Gallery min="22rem">
          <GalleryItem name="GlowBackground" hint="Animated mesh behind hero content.">
            <GlowDemo label="Default — theme primary blobs" />
          </GalleryItem>
          <GalleryItem name="GlowBackground" hint="Recolor with a CSS filter, no fork.">
            <GlowDemo
              className="[filter:hue-rotate(120deg)_saturate(1.2)]"
              label="Tinted — hue-rotate(120deg)"
            />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Glyph-scale transition">
        <Gallery>
          <GalleryItem name="Swap" hint="Toggle two icons; click to animate.">
            <div className="flex h-40 items-center gap-6 rounded-md border px-4">
              <SwapHost animation="fade" />
              <SwapHost animation="rotate" />
              <SwapHost animation="flip" />
              <SwapHost animation="scale" />
            </div>
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};
