import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Slider, Label } from '@djangocfg/ui-core/components';

const meta: Meta<typeof Slider> = {
  title: 'Packages/UI Core/Forms/Slider',
  component: Slider,
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof Slider>;

export const Default: Story = {
  render: () => (
    <div className="grid w-64 gap-2">
      <Label>Volume</Label>
      <Slider defaultValue={[50]} max={100} step={1} />
    </div>
  ),
};

export const Range: Story = {
  render: () => (
    <div className="grid w-64 gap-2">
      <Label>Price range</Label>
      <Slider defaultValue={[20, 80]} max={100} step={5} />
    </div>
  ),
};

function WithLabelHost() {
  const [value, setValue] = useState([25]);
  return (
    <div className="grid w-64 gap-2">
      <div className="flex justify-between">
        <Label>Volume</Label>
        <span className="text-sm text-muted-foreground">{value[0]}%</span>
      </div>
      <Slider value={value} onValueChange={setValue} max={100} step={1} />
    </div>
  );
}

export const WithLabel: Story = { render: () => <WithLabelHost /> };

export const Steps: Story = {
  render: () => (
    <div className="grid w-64 gap-6">
      {[1, 10, 25].map((s) => (
        <div key={s} className="grid gap-2">
          <Label>Step: {s}</Label>
          <Slider defaultValue={[50]} max={100} step={s} />
        </div>
      ))}
    </div>
  ),
};

export const Disabled: Story = {
  render: () => (
    <div className="w-64">
      <Slider defaultValue={[50]} max={100} disabled />
    </div>
  ),
};

function VerticalHost() {
  const [value, setValue] = useState([70]);
  return (
    <div className="flex flex-col items-center gap-2">
      <span className="text-sm text-muted-foreground">{value[0]}%</span>
      <Slider
        orientation="vertical"
        value={value}
        onValueChange={setValue}
        max={100}
        step={5}
        className="h-32"
      />
      <Label>Volume</Label>
    </div>
  );
}

export const Vertical: Story = { render: () => <VerticalHost /> };
