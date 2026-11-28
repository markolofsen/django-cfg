import { useEffect, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Progress } from '@djangocfg/ui-core/components';

const meta: Meta<typeof Progress> = {
  title: 'Packages/UI Core/Data/Progress',
  component: Progress,
  tags: ['autodocs'],
  argTypes: {
    value: { control: { type: 'range', min: 0, max: 100, step: 1 } },
  },
  args: { value: 60 },
};

export default meta;

type Story = StoryObj<typeof Progress>;

export const Default: Story = {
  render: (args) => (
    <div className="w-80">
      <Progress {...args} />
    </div>
  ),
};

export const Values: Story = {
  render: () => (
    <div className="w-80 space-y-4">
      {[0, 25, 50, 75, 100].map((v) => (
        <div key={v} className="space-y-1">
          <span className="text-sm">{v}%</span>
          <Progress value={v} />
        </div>
      ))}
    </div>
  ),
};

export const Stack: Story = {
  render: () => (
    <div className="grid w-80 gap-3">
      {[25, 50, 75, 100].map((v) => (
        <div key={v} className="grid gap-1.5">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Step {v / 25}</span>
            <span>{v}%</span>
          </div>
          <Progress value={v} />
        </div>
      ))}
    </div>
  ),
};

function AnimatedProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const t = setInterval(() => {
      setProgress((p) => (p >= 100 ? 0 : p + 10));
    }, 500);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="w-80 space-y-2">
      <div className="flex justify-between text-sm">
        <span>Loading…</span>
        <span>{progress}%</span>
      </div>
      <Progress value={progress} />
    </div>
  );
}

export const Animated: Story = {
  render: () => <AnimatedProgress />,
};

export const WithLabel: Story = {
  render: () => (
    <div className="w-80 space-y-2">
      <div className="flex justify-between text-sm">
        <span>Upload progress</span>
        <span>75%</span>
      </div>
      <Progress value={75} />
    </div>
  ),
};
