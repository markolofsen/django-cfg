import type { Meta, StoryObj } from '@storybook/react-vite';
import { LazyImageViewer as ImageViewer } from '.';

/**
 * Lightbox — the macOS Quick-Look-grade fullscreen presentation used when an
 * image attachment is clicked in chat (`ImageLightboxProvider`).
 *
 * What to verify here:
 * - Trackpad pinch (or wheel + Ctrl) zooms 1:1 with the gesture, anchored to
 *   the FOCAL POINT under the cursor — the point under your fingers stays put.
 * - Double-click toggles fit ↔ zoomed (toward the click point); drag pans when
 *   zoomed; keyboard +/-/0 zoom, arrows pan / navigate, Esc closes.
 * - Chrome (close, prev/next, counter + live zoom %) floats on liquid-glass
 *   and FADES when the pointer rests, returning on the slightest movement.
 * - Backdrop is a deep blurred vibrancy surface — the image floats with a soft
 *   drop shadow. No checkerboard, no rotate/flip slab.
 */

const SAMPLES = [
  {
    file: { name: 'mountains.jpg', path: 'mountains' },
    src: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=2000',
  },
  {
    file: { name: 'forest.jpg', path: 'forest' },
    src: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=2000',
  },
  {
    file: { name: 'lake.jpg', path: 'lake' },
    src: 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=2000',
  },
  {
    file: { name: 'city.jpg', path: 'city' },
    src: 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=2000',
  },
];

const meta = {
  title: 'Widgets/Media/Lightbox',
  component: ImageViewer,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          'macOS-grade fullscreen lightbox: focal-point pinch/wheel zoom, idle-fading liquid-glass chrome, blurred vibrancy backdrop. This is what chat opens on an image click.',
      },
    },
  },
} satisfies Meta<typeof ImageViewer>;

export default meta;

type Story = StoryObj<typeof meta>;

// A textured backdrop behind the lightbox so the backdrop blur/vibrancy is
// visible (mirrors a real chat page sitting behind the dialog).
const renderFullBleed: Story['render'] = (args) => (
  <div className="relative h-screen w-screen overflow-hidden">
    <div
      aria-hidden
      className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,#6366f1_0%,transparent_40%),radial-gradient(circle_at_80%_70%,#ec4899_0%,transparent_45%),radial-gradient(circle_at_50%_90%,#22d3ee_0%,transparent_40%)] opacity-60"
    />
    <div className="absolute inset-0">
      <ImageViewer {...args} />
    </div>
  </div>
);

export const Gallery: Story = {
  args: { images: SAMPLES, initialIndex: 0, lightbox: true, autoFocus: true },
  render: renderFullBleed,
};

export const LongFilename: Story = {
  args: {
    images: [
      {
        file: {
          name: 'screencapture-referee-id-2026-06-11-at-14.29.07-very-long-name.png',
          path: 'screencapture',
        },
        src: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=2000',
      },
      ...SAMPLES.slice(1),
    ],
    initialIndex: 0,
    lightbox: true,
    autoFocus: true,
  },
  render: renderFullBleed,
  parameters: {
    docs: {
      description: {
        story:
          'Long filename (60+ chars) in the top-left chip. The pill caps its width (clamp 8rem–40vw–28rem) and middle-truncates Finder-style — the start AND the .png extension stay readable ("screencapture-referee…long-name.png"). It never overlaps the close button, and hover shows the full name via the title tooltip.',
      },
    },
  },
};

export const Single: Story = {
  args: { images: SAMPLES.slice(0, 1), lightbox: true, autoFocus: true },
  render: renderFullBleed,
  parameters: {
    docs: {
      description: {
        story:
          'Single image — no prev/next, no counter. The only chrome is the close button (and the zoom % pill once you zoom).',
      },
    },
  },
};
