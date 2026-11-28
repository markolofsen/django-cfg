import type { Meta, StoryObj } from '@storybook/react-vite';
import { Masonry, MasonryItem } from '../Masonry';

const meta = {
  title: 'Widgets/Data/Masonry',
  component: Masonry,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Virtualised masonry layout with column balancing and ResizeObserver. ' +
          'Pass either `columnWidth` (responsive — Masonry derives column count from ' +
          'its measured width) or `columnCount` (fixed — Masonry derives column width). ' +
          'Item height is driven by content; do not put inline `height` on `<MasonryItem>`.',
      },
    },
  },
  argTypes: {
    columnWidth: { control: 'number' },
    columnCount: { control: 'number' },
    gap: { control: 'number' },
  },
} satisfies Meta<typeof Masonry>;

export default meta;
type Story = StoryObj<typeof meta>;

const items = [
  { id: 1, title: 'The 900',          body: 'Spin 900 degrees in the air.' },
  { id: 2, title: 'Indy Backflip',    body: 'Backflip in the air while grabbing the board with your back hand.' },
  { id: 3, title: 'Pizza Guy',        body: 'Flip the board like a pizza.' },
  { id: 4, title: 'Rocket Air',       body: 'Grab the nose of your board and point it straight up to the sky.' },
  { id: 5, title: 'Kickflip Backflip', body: 'A kickflip while doing a backflip simultaneously — peak nonsense.' },
  { id: 6, title: 'FS 540',           body: 'Spin frontside 540 degrees in the air.' },
  { id: 7, title: 'Madonna',          body: 'Tail-grab one-foot indy variant, popularised in vert ramps.' },
  { id: 8, title: 'Christ Air',       body: 'Spread your arms and legs out wide while in the air — the classic vert pose.' },
  { id: 9, title: 'Heelflip',         body: 'Flip the board outward with the heel while ollieing.' },
];

export const Default: Story = {
  render: () => (
    <Masonry columnCount={3} gap={12}>
      {items.map((item) => (
        <MasonryItem
          key={item.id}
          className="flex flex-col gap-1 rounded-md border bg-card p-4 text-card-foreground shadow-xs"
        >
          <div className="font-medium text-sm leading-tight sm:text-base">{item.title}</div>
          <span className="text-sm text-muted-foreground">{item.body}</span>
        </MasonryItem>
      ))}
    </Masonry>
  ),
};

export const ResponsiveByColumnWidth: Story = {
  render: () => (
    <Masonry columnWidth={240} gap={12}>
      {items.map((item) => (
        <MasonryItem
          key={item.id}
          className="flex flex-col gap-1 rounded-md border bg-card p-4 text-card-foreground shadow-xs"
        >
          <div className="font-medium text-sm leading-tight sm:text-base">{item.title}</div>
          <span className="text-sm text-muted-foreground">{item.body}</span>
        </MasonryItem>
      ))}
    </Masonry>
  ),
};
