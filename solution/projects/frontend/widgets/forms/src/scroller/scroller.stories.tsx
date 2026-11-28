import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Scroller,
  ScrollerItem,
} from '.';

const meta = {
  title: 'Widgets/Forms/Scroller',
  component: Scroller,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A smooth scroll container with optional snap points and scroll indicators.',
      },
    },
  },
  argTypes: {
    orientation: { control: 'select', options: ['horizontal', 'vertical'] },
    snap: { control: 'boolean' },
    showIndicators: { control: 'boolean' },
    hideScrollbar: { control: 'boolean' },
  },
  args: {
    children: null,
  },
} satisfies Meta<typeof Scroller>;

export default meta;
type Story = StoryObj<typeof meta>;

const items = Array.from({ length: 12 }, (_, i) => ({
  id: i,
  title: `Item ${i + 1}`,
  // Categorical tints for the demo rows — no status meaning, so the chart
  // palette rather than success/warning/destructive.
  color: ['bg-chart-1/20', 'bg-chart-2/20', 'bg-chart-3/20', 'bg-chart-4/20', 'bg-chart-5/20'][i % 5],
}));

export const Default: Story = {
  render: () => (
    <Scroller className="w-[400px]" orientation="horizontal">
      {items.map((item) => (
        <ScrollerItem key={item.id} className="w-32 p-2">
          <div className={`rounded-md ${item.color} p-4 text-center text-sm font-medium`}>
            {item.title}
          </div>
        </ScrollerItem>
      ))}
    </Scroller>
  ),
};

export const WithSnap: Story = {
  render: () => (
    <Scroller className="w-[400px]" orientation="horizontal" snap showIndicators>
      {items.map((item) => (
        <ScrollerItem key={item.id} className="w-32 p-2" snapAlign="start">
          <div className={`rounded-md ${item.color} p-4 text-center text-sm font-medium`}>
            {item.title}
          </div>
        </ScrollerItem>
      ))}
    </Scroller>
  ),
};

/**
 * `snapAlign` on the parent is the default every item inherits. Nothing here
 * sets it per item — before the snap classes were static, this story and
 * `WithSnap` rendered identically because neither snapped at all.
 */
export const SnapAlignCenter: Story = {
  render: () => (
    <Scroller className="w-[400px]" orientation="horizontal" snap snapAlign="center" showIndicators>
      {items.map((item) => (
        <ScrollerItem key={item.id} className="w-32 p-2">
          <div className={`rounded-md ${item.color} p-4 text-center text-sm font-medium`}>
            {item.title}
          </div>
        </ScrollerItem>
      ))}
    </Scroller>
  ),
};

/** An item's own `snapAlign` overrides the parent's — item 3 lands at the end. */
export const SnapAlignOverride: Story = {
  render: () => (
    <Scroller className="w-[400px]" orientation="horizontal" snap snapAlign="start" showIndicators>
      {items.map((item) => (
        <ScrollerItem
          key={item.id}
          className="w-32 p-2"
          snapAlign={item.id === 2 ? 'end' : undefined}
        >
          <div className={`rounded-md ${item.color} p-4 text-center text-sm font-medium`}>
            {item.title}
          </div>
        </ScrollerItem>
      ))}
    </Scroller>
  ),
};

/** Snap follows `orientation`: this one snaps on y, not x. */
export const VerticalSnap: Story = {
  render: () => (
    <Scroller className="h-[300px] w-[200px]" orientation="vertical" snap snapAlign="center">
      {items.map((item) => (
        <ScrollerItem key={item.id} className="p-2">
          <div className={`rounded-md ${item.color} p-4 text-center text-sm font-medium`}>
            {item.title}
          </div>
        </ScrollerItem>
      ))}
    </Scroller>
  ),
};

export const Vertical: Story = {
  render: () => (
    <Scroller className="h-[300px] w-[200px]" orientation="vertical" showIndicators>
      {items.map((item) => (
        <ScrollerItem key={item.id} className="p-2">
          <div className={`rounded-md ${item.color} p-4 text-center text-sm font-medium`}>
            {item.title}
          </div>
        </ScrollerItem>
      ))}
    </Scroller>
  ),
};

export const WithScrollbar: Story = {
  render: () => (
    <Scroller className="w-[400px]" orientation="horizontal" hideScrollbar={false}>
      {items.map((item) => (
        <ScrollerItem key={item.id} className="w-32 p-2">
          <div className={`rounded-md ${item.color} p-4 text-center text-sm font-medium`}>
            {item.title}
          </div>
        </ScrollerItem>
      ))}
    </Scroller>
  ),
};
