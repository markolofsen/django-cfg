import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { ChevronsUpDown } from 'lucide-react';
import {
  Button,
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Collapsible',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

function CollapsibleDemo() {
  const [open, setOpen] = useState(false);
  return (
    <Collapsible open={open} onOpenChange={setOpen} className="w-80 space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold">@djangocfg starred</h4>
        <CollapsibleTrigger asChild>
          <Button variant="ghost" size="sm">
            <ChevronsUpDown className="h-4 w-4" />
          </Button>
        </CollapsibleTrigger>
      </div>
      <div className="rounded-md border border-border px-4 py-2 font-mono text-sm">
        @djangocfg/ui-core
      </div>
      <CollapsibleContent className="space-y-2">
        <div className="rounded-md border border-border px-4 py-2 font-mono text-sm">
          @djangocfg/ui-tools
        </div>
        <div className="rounded-md border border-border px-4 py-2 font-mono text-sm">
          @djangocfg/layouts
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}

export const Default: Story = { render: () => <CollapsibleDemo /> };

function OpenByDefaultDemo() {
  const [open, setOpen] = useState(true);
  return (
    <Collapsible open={open} onOpenChange={setOpen} className="w-80 space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold">Notifications</h4>
        <CollapsibleTrigger asChild>
          <Button variant="ghost" size="sm">
            {open ? 'Hide' : 'Show'}
          </Button>
        </CollapsibleTrigger>
      </div>
      <CollapsibleContent className="space-y-2">
        {[
          'You have 3 new notifications',
          'Your order has been shipped',
          'New comment on your post',
        ].map((m) => (
          <div key={m} className="rounded-md border px-4 py-3 text-sm">
            {m}
          </div>
        ))}
      </CollapsibleContent>
    </Collapsible>
  );
}

export const OpenByDefault: Story = { render: () => <OpenByDefaultDemo /> };

export const Simple: Story = {
  render: () => (
    <Collapsible className="w-80">
      <CollapsibleTrigger asChild>
        <Button variant="outline" className="w-full justify-between">
          Can I use this in my project?
          <ChevronsUpDown className="h-4 w-4" />
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent className="pt-2">
        <p className="px-1 text-sm text-muted-foreground">
          Yes! Free for personal and commercial use. No attribution required.
        </p>
      </CollapsibleContent>
    </Collapsible>
  ),
};

export const Multiple: Story = {
  render: () => (
    <div className="w-80 space-y-2">
      {[1, 2, 3].map((n) => (
        <Collapsible key={n}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full justify-between">
              Section {n}
              <ChevronsUpDown className="h-4 w-4" />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="px-4 py-2">
            Content for section {n}
          </CollapsibleContent>
        </Collapsible>
      ))}
    </div>
  ),
};
