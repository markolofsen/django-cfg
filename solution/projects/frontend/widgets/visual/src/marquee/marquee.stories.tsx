import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Marquee,
  MarqueeContent,
  MarqueeItem,
  MarqueeEdge,
} from '.';

const meta = {
  title: 'Widgets/Visual/Marquee',
  component: Marquee,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A smooth scrolling marquee with pause-on-hover, auto-fill, and edge gradients.',
      },
    },
  },
  argTypes: {
    side: { control: 'select', options: ['left', 'right', 'top', 'bottom'] },
    speed: { control: 'number' },
    pauseOnHover: { control: 'boolean' },
    reverse: { control: 'boolean' },
    autoFill: { control: 'boolean' },
  },
} satisfies Meta<typeof Marquee>;

export default meta;
type Story = StoryObj<typeof meta>;

const tags = ['React', 'TypeScript', 'Tailwind', 'Next.js', 'Vite', 'Node.js', 'PostgreSQL'];

export const Default: Story = {
  render: () => (
    <Marquee className="w-full">
      <MarqueeContent>
        {tags.map((tag) => (
          <MarqueeItem key={tag} className="rounded-full border px-4 py-1 text-sm">
            {tag}
          </MarqueeItem>
        ))}
      </MarqueeContent>
    </Marquee>
  ),
};

export const PauseOnHover: Story = {
  render: () => (
    <Marquee pauseOnHover className="w-full">
      <MarqueeContent>
        {tags.map((tag) => (
          <MarqueeItem key={tag} className="rounded-full border px-4 py-1 text-sm">
            {tag}
          </MarqueeItem>
        ))}
      </MarqueeContent>
    </Marquee>
  ),
};

export const Reverse: Story = {
  render: () => (
    <Marquee reverse className="w-full">
      <MarqueeContent>
        {tags.map((tag) => (
          <MarqueeItem key={tag} className="rounded-full border px-4 py-1 text-sm">
            {tag}
          </MarqueeItem>
        ))}
      </MarqueeContent>
    </Marquee>
  ),
};

export const Vertical: Story = {
  render: () => (
    <Marquee side="top" className="h-48">
      <MarqueeContent>
        {tags.map((tag) => (
          <MarqueeItem key={tag} className="rounded-full border px-4 py-1 text-sm">
            {tag}
          </MarqueeItem>
        ))}
      </MarqueeContent>
    </Marquee>
  ),
};

export const WithEdges: Story = {
  render: () => (
    <div className="relative w-full">
      <Marquee className="w-full">
        <MarqueeContent>
          {tags.map((tag) => (
            <MarqueeItem key={tag} className="rounded-full border px-4 py-1 text-sm">
              {tag}
            </MarqueeItem>
          ))}
        </MarqueeContent>
      </Marquee>
      <MarqueeEdge side="left" />
      <MarqueeEdge side="right" />
    </div>
  ),
};

export const AutoFill: Story = {
  render: () => (
    <Marquee autoFill className="w-full">
      <MarqueeContent>
        <MarqueeItem className="rounded-full bg-primary px-4 py-1 text-sm text-primary-foreground">
          Only one item — auto-filled
        </MarqueeItem>
      </MarqueeContent>
    </Marquee>
  ),
};
