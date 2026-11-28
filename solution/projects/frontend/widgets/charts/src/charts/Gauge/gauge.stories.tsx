import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Gauge,
  GaugeCombined,
  GaugeIndicator,
  GaugeTrack,
  GaugeRange,
  GaugeValueText,
  GaugeLabel,
} from '.';

const meta = {
  title: 'Widgets/Charts/Gauge',
  component: Gauge,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'An SVG-based gauge/meter for displaying values within a range.',
      },
    },
  },
  argTypes: {
    value: { control: 'number' },
    min: { control: 'number' },
    max: { control: 'number' },
    size: { control: 'number' },
    thickness: { control: 'number' },
  },
} satisfies Meta<typeof Gauge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => <GaugeCombined value={65} />,
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-6">
      <GaugeCombined value={60} size={64} thickness={4} />
      <GaugeCombined value={60} size={96} thickness={6} />
      <GaugeCombined value={60} size={128} thickness={8} />
      <GaugeCombined value={60} size={160} thickness={10} />
    </div>
  ),
};

export const Indeterminate: Story = {
  render: () => <GaugeCombined />,
};

export const Complete: Story = {
  render: () => <GaugeCombined value={100} />,
};

export const CustomRange: Story = {
  render: () => <GaugeCombined value={750} min={0} max={1000} />,
};

export const Semicircle: Story = {
  render: () => (
    <Gauge value={72} size={128} startAngle={0} endAngle={180}>
      <GaugeIndicator>
        <GaugeTrack />
        <GaugeRange />
      </GaugeIndicator>
      <GaugeValueText />
      <GaugeLabel>Score</GaugeLabel>
    </Gauge>
  ),
};

export const Colors: Story = {
  render: () => (
    <div className="flex items-center gap-6">
      <Gauge value={50} size={96}>
        <GaugeIndicator>
          <GaugeTrack className="text-muted-foreground/20" />
          <GaugeRange className="text-chart-1" />
        </GaugeIndicator>
        <GaugeValueText />
      </Gauge>
      <Gauge value={75} size={96}>
        <GaugeIndicator>
          <GaugeTrack className="text-muted-foreground/20" />
          <GaugeRange className="text-chart-2" />
        </GaugeIndicator>
        <GaugeValueText />
      </Gauge>
      <Gauge value={30} size={96}>
        <GaugeIndicator>
          <GaugeTrack className="text-muted-foreground/20" />
          <GaugeRange className="text-chart-3" />
        </GaugeIndicator>
        <GaugeValueText />
      </Gauge>
    </div>
  ),
};
