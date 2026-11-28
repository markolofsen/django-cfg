import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Sparkline,
  type SparklineColor,
  type SparklineVariant,
} from '.';

const COLORS: SparklineColor[] = ['primary', 'success', 'warning', 'destructive', 'info'];
const VARIANTS: SparklineVariant[] = ['line', 'area', 'bar'];

// Synthetic but realistic sample data — vaguely up-trending with noise.
const SAMPLE = [
  12, 14, 11, 18, 22, 19, 24, 28, 26, 31, 35, 33, 38, 42, 40, 46, 49, 52, 50, 58,
];

const meta = {
  title: 'Widgets/Charts/Sparkline',
  component: Sparkline,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Tiny inline SVG sparkline. Pure SVG, no charting deps. Color resolves through the theme palette via `useThemeColor()` — semantic tokens only.',
      },
    },
  },
  argTypes: {
    variant: { control: 'select', options: VARIANTS },
    color: { control: 'select', options: COLORS },
    width: { control: { type: 'number', min: 40, max: 480 } },
    height: { control: { type: 'number', min: 16, max: 160 } },
    strokeWidth: { control: { type: 'number', min: 0.5, max: 4, step: 0.25 } },
    showEndpoint: { control: 'boolean' },
    showBaseline: { control: 'boolean' },
  },
} satisfies Meta<typeof Sparkline>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { data: SAMPLE },
};

export const Variants: Story = {
  args: { data: SAMPLE },
  render: () => (
    <div className="flex flex-wrap items-center gap-6">
      {VARIANTS.map((variant) => (
        <div key={variant} className="flex flex-col items-center gap-1">
          <Sparkline data={SAMPLE} variant={variant} />
          <span className="text-xs text-muted-foreground">{variant}</span>
        </div>
      ))}
    </div>
  ),
};

export const Colors: Story = {
  args: { data: SAMPLE },
  render: () => (
    <div className="flex flex-wrap items-center gap-6">
      {COLORS.map((color) => (
        <div key={color} className="flex flex-col items-center gap-1">
          <Sparkline data={SAMPLE} variant="area" color={color} />
          <span className="text-xs text-muted-foreground">{color}</span>
        </div>
      ))}
    </div>
  ),
};

export const Area: Story = {
  args: { data: SAMPLE, variant: 'area', color: 'success' },
};

export const Bars: Story = {
  args: { data: SAMPLE, variant: 'bar', color: 'info', width: 160, height: 40 },
};

export const WithBaseline: Story = {
  args: { data: SAMPLE, variant: 'line', showBaseline: true, width: 200, height: 48 },
};

export const ObjectData: Story = {
  args: {
    data: SAMPLE.map((value, i) => ({ value, label: `Day ${i + 1}` })),
    variant: 'area',
    color: 'primary',
    ariaLabel: 'Daily metric trend',
  },
};

export const Empty: Story = {
  args: { data: [] },
};
