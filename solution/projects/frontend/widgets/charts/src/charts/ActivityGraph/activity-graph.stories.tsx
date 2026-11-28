import type { Meta, StoryObj } from '@storybook/react-vite';
import { ActivityGraph, type ActivityEntry } from '.';

/**
 * Generate `days` of synthetic entries ending today. Counts are biased
 * to leave a healthy mix of empty / low / mid / high cells so the five
 * intensity buckets are all visible.
 */
function makeData(days: number, seed = 1): ActivityEntry[] {
  const out: ActivityEntry[] = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  let rng = seed;
  for (let i = days - 1; i >= 0; i--) {
    rng = (rng * 1664525 + 1013904223) % 0xffffffff;
    const r = rng / 0xffffffff;
    // 30% empty, 70% in 1..20 with a steep tail.
    const count = r < 0.3 ? 0 : Math.floor(Math.pow(r, 2.2) * 20) + 1;
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    out.push({ date: d.toISOString().slice(0, 10), count });
  }
  return out;
}

const yearData = makeData(52 * 7, 42);

const meta = {
  title: 'Widgets/Charts/ActivityGraph',
  component: ActivityGraph,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'GitHub-style contribution heatmap. Cell colors resolve through the active theme `primary` token (via `useThemeColor` + `alpha`) — switching the theme preset re-tints the whole grid automatically.',
      },
    },
  },
  argTypes: {
    weeks: { control: { type: 'number', min: 4, max: 104, step: 1 } },
    blockSize: { control: { type: 'number', min: 4, max: 40, step: 1 } },
    blockRadius: { control: { type: 'number', min: 0, max: 12, step: 1 } },
  },
} satisfies Meta<typeof ActivityGraph>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { data: yearData },
};

export const FixedBlockSize: Story = {
  args: { data: yearData, blockSize: 12, blockRadius: 3 },
};

export const ShortRange: Story = {
  args: { data: makeData(12 * 7, 7), weeks: 12 },
};

export const Empty: Story = {
  args: { data: [] },
};
