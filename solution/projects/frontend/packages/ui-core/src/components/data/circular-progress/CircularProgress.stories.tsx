import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  CircularProgress,
  CircularProgressCombined,
  CircularProgressIndicator,
  CircularProgressRange,
  CircularProgressTrack,
  CircularProgressValueText,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/CircularProgress',
  component: CircularProgress,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'Accessible circular progress indicator with SVG-based rendering.',
      },
    },
  },
  argTypes: {
    value: { control: 'number' },
    max: { control: 'number' },
    min: { control: 'number' },
    size: { control: 'number' },
    thickness: { control: 'number' },
  },
} satisfies Meta<typeof CircularProgress>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <CircularProgressCombined value={65} />
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-6">
      <CircularProgressCombined value={60} size={32} thickness={3} />
      <CircularProgressCombined value={60} size={48} />
      <CircularProgressCombined value={60} size={64} thickness={6} />
      <CircularProgressCombined value={60} size={96} thickness={8} />
    </div>
  ),
};

export const Indeterminate: Story = {
  render: () => (
    <CircularProgressCombined />
  ),
};

export const Complete: Story = {
  render: () => (
    <CircularProgressCombined value={100} />
  ),
};

export const CustomMax: Story = {
  render: () => (
    <CircularProgressCombined value={750} max={1000} />
  ),
};

export const CustomLabel: Story = {
  render: () => (
    <CircularProgress value={72} size={64}>
      <CircularProgressIndicator>
        <CircularProgressTrack />
        <CircularProgressRange />
      </CircularProgressIndicator>
      <CircularProgressValueText>
        <span className="text-lg font-bold">72%</span>
      </CircularProgressValueText>
    </CircularProgress>
  ),
};

export const Colors: Story = {
  render: () => (
    <div className="flex items-center gap-6">
      <CircularProgress value={50}>
        <CircularProgressIndicator>
          <CircularProgressTrack className="text-muted-foreground/20" />
          <CircularProgressRange className="text-chart-2" />
        </CircularProgressIndicator>
        <CircularProgressValueText />
      </CircularProgress>
      <CircularProgress value={75}>
        <CircularProgressIndicator>
          <CircularProgressTrack className="text-muted-foreground/20" />
          <CircularProgressRange className="text-chart-3" />
        </CircularProgressIndicator>
        <CircularProgressValueText />
      </CircularProgress>
      <CircularProgress value={30}>
        <CircularProgressIndicator>
          <CircularProgressTrack className="text-muted-foreground/20" />
          <CircularProgressRange className="text-chart-4" />
        </CircularProgressIndicator>
        <CircularProgressValueText />
      </CircularProgress>
    </div>
  ),
};
