import type { Meta, StoryObj } from '@storybook/react-vite';
import { LazyImageViewer as ImageViewer } from '.';

/**
 * Hooks demo for ImageViewer.
 *
 * `useImageTransform` and `useImageLoading` live inside the package
 * (`src/image-viewer/hooks`) but are not currently
 * re-exported from any public subpath. Storybook here demonstrates the
 * same surface area through the public `LazyImageViewer` component —
 * which internally consumes both hooks — by mounting it inside a custom
 * layout chrome that mimics what an integrator would build with the
 * hooks directly: framed canvas, caption strip, secondary action bar.
 *
 * Once the hooks ship on a public subpath (e.g. `./image-viewer/hooks`)
 * this file should be upgraded to drive the hook directly via custom
 * zoom buttons.
 */

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
];

const meta = {
  title: 'Widgets/Media/Hooks',
  component: ImageViewer,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Demonstrates how an app shell can wrap `ImageViewer` with custom chrome. The viewer drives all transform/zoom state internally via `useImageTransform` + `useImageLoading`; the surrounding layout is owned by the consumer.',
      },
    },
  },
} satisfies Meta<typeof ImageViewer>;

export default meta;

type Story = StoryObj<typeof meta>;

export const CustomLayout: Story = {
  args: { images: SAMPLES, initialIndex: 0 },
  render: (args) => (
    <div className="flex w-[760px] flex-col gap-2 rounded-lg border border-border bg-card p-3 shadow-sm">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className="font-medium uppercase tracking-wide">Asset preview</span>
        <span>
          {args.images.length} image{args.images.length === 1 ? '' : 's'}
        </span>
      </div>
      <div className="h-[480px] overflow-hidden rounded-md border border-border bg-background">
        <ImageViewer {...args} />
      </div>
      <p className="text-xs text-muted-foreground">
        Toolbar, zoom, and gallery state come from the hooks consumed inside the viewer. The
        outer card is consumer-owned chrome.
      </p>
    </div>
  ),
};

export const ScopedFrame: Story = {
  args: { images: SAMPLES.slice(0, 1) },
  render: (args) => (
    <div className="grid w-[760px] grid-cols-[1fr_220px] gap-3">
      <div className="h-[420px] overflow-hidden rounded-md border border-border bg-background">
        <ImageViewer {...args} />
      </div>
      <aside className="rounded-md border border-border bg-card p-3 text-xs">
        <h4 className="mb-2 text-sm font-semibold">Hook surface</h4>
        <ul className="space-y-1 text-muted-foreground">
          <li>
            <code>useImageTransform</code> &mdash; rotation + flipH/flipV state, exposes
            <code> transformStyle</code>.
          </li>
          <li>
            <code>useImageLoading</code> &mdash; LQIP, progressive load, intrinsic size.
          </li>
        </ul>
      </aside>
    </div>
  ),
};
