import type { Meta, StoryObj } from '@storybook/react-vite';
import { HelpCircle, Plus, Settings } from 'lucide-react';
import {
  Button,
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Overlay/Tooltip',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          '`TooltipProvider` is already mounted at the Storybook preview level, so individual stories don\'t wrap with one.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant="outline">Hover me</Button>
      </TooltipTrigger>
      <TooltipContent>Reveal the secret message</TooltipContent>
    </Tooltip>
  ),
};

export const Positions: Story = {
  render: () => (
    <div className="flex gap-4 p-10">
      {(['top', 'right', 'bottom', 'left'] as const).map((side) => (
        <Tooltip key={side}>
          <TooltipTrigger asChild>
            <Button variant="outline">{side}</Button>
          </TooltipTrigger>
          <TooltipContent side={side}>{side} tooltip</TooltipContent>
        </Tooltip>
      ))}
    </div>
  ),
};

export const WithIcons: Story = {
  render: () => (
    <div className="flex gap-2">
      {[
        { icon: Plus, label: 'Add new item' },
        { icon: Settings, label: 'Settings' },
        { icon: HelpCircle, label: 'Help & Support' },
      ].map(({ icon: Icon, label }, i) => (
        <Tooltip key={i}>
          <TooltipTrigger asChild>
            <Button size="icon" variant="outline">
              <Icon className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>{label}</TooltipContent>
        </Tooltip>
      ))}
    </div>
  ),
};

export const WithShortcut: Story = {
  render: () => (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant="outline">Save</Button>
      </TooltipTrigger>
      <TooltipContent className="flex items-center gap-2">
        <span>Save document</span>
        <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
          <span className="text-xs">⌘</span>S
        </kbd>
      </TooltipContent>
    </Tooltip>
  ),
};
