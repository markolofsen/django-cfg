import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Bug, Flame, Rocket, Star, Trophy, Zap } from 'lucide-react';
import {
  Label,
  MultiSelectPro,
  type MultiSelectProOption,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/MultiSelectPro',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Multi-select with icon support, animated badges, grouped options and Select-All. Use `MultiSelectProAsync` when options come from a backend.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

const OPTIONS: MultiSelectProOption[] = [
  { value: 'bug', label: 'Bug', icon: Bug, description: 'Issue tracker' },
  { value: 'feature', label: 'Feature', icon: Star, description: 'New capability' },
  { value: 'perf', label: 'Performance', icon: Zap, description: 'Optimisation' },
  { value: 'rocket', label: 'Launch', icon: Rocket },
  { value: 'fire', label: 'Hotfix', icon: Flame },
  { value: 'trophy', label: 'Milestone', icon: Trophy },
];

function PlaygroundHost(args: {
  hideSelectAll: boolean;
  animation: number;
  maxCount: number;
  searchable: boolean;
  closeOnSelect: boolean;
  variant: 'default' | 'secondary' | 'destructive' | 'inverted';
}) {
  const [value, setValue] = useState<string[]>(['bug', 'feature']);
  return (
    <div className="grid w-96 gap-1.5">
      <Label>Labels</Label>
      <MultiSelectPro
        options={OPTIONS}
        defaultValue={value}
        onValueChange={setValue}
        placeholder="Pick labels…"
        hideSelectAll={args.hideSelectAll}
        animation={args.animation}
        maxCount={args.maxCount}
        searchable={args.searchable}
        closeOnSelect={args.closeOnSelect}
        variant={args.variant}
      />
      <p className="text-xs text-muted-foreground">Selected: {value.join(', ') || '(none)'}</p>
    </div>
  );
}

export const Playground: Story = {
  argTypes: {
    hideSelectAll: { control: 'boolean', description: 'Hide the "Select All" row' },
    animation: {
      control: { type: 'range', min: 0, max: 3, step: 0.5 },
      description: 'Badge animation delay multiplier (0 = no animation)',
    },
    maxCount: {
      control: { type: 'number', min: 1, max: 6 },
      description: 'Max badges visible before "+N more"',
    },
    searchable: { control: 'boolean' },
    closeOnSelect: { control: 'boolean', description: 'Close popover after a pick' },
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'destructive', 'inverted'],
    },
  },
  args: {
    hideSelectAll: false,
    animation: 0,
    maxCount: 3,
    searchable: true,
    closeOnSelect: false,
    variant: 'default',
  },
  render: (args) => {
    const a = args as {
      hideSelectAll?: boolean;
      animation?: number;
      maxCount?: number;
      searchable?: boolean;
      closeOnSelect?: boolean;
      variant?: 'default' | 'secondary' | 'destructive' | 'inverted';
    };
    return PlaygroundHost({
      hideSelectAll: a.hideSelectAll ?? false,
      animation: a.animation ?? 0,
      maxCount: a.maxCount ?? 3,
      searchable: a.searchable ?? true,
      closeOnSelect: a.closeOnSelect ?? false,
      variant: a.variant ?? 'default',
    });
  },
};

function WithIconsHost() {
  const [value, setValue] = useState<string[]>(['rocket', 'fire']);
  return (
    <div className="grid w-96 gap-1.5">
      <Label>Labels with icons</Label>
      <MultiSelectPro
        options={OPTIONS}
        defaultValue={value}
        onValueChange={setValue}
        placeholder="Pick labels…"
        animation={1}
      />
    </div>
  );
}

export const WithIcons: Story = {
  render: () => <WithIconsHost />,
};

function ClearableHost() {
  const [value, setValue] = useState<string[]>(['bug', 'feature', 'perf']);
  return (
    <div className="grid w-96 gap-2">
      <Label>Labels (click X on the trigger to clear all)</Label>
      <MultiSelectPro
        options={OPTIONS}
        defaultValue={value}
        onValueChange={setValue}
        placeholder="Pick labels…"
        maxCount={5}
      />
      <p className="text-xs text-muted-foreground">Selected: {value.length}</p>
    </div>
  );
}

export const Clearable: Story = {
  render: () => <ClearableHost />,
};
