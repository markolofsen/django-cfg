import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Calendar, Calculator, Settings, Smile, User } from 'lucide-react';
import {
  Button,
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Command',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Searchable command palette (cmdk). Pair with `CommandDialog` to render it inside a `Dialog` for global ⌘K shortcuts.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Command className="w-[420px] rounded-lg border border-border">
      <CommandInput placeholder="Type a command or search…" />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Suggestions">
          <CommandItem>
            <Calendar className="mr-2 h-4 w-4" /> Calendar
          </CommandItem>
          <CommandItem>
            <Smile className="mr-2 h-4 w-4" /> Search emoji
          </CommandItem>
          <CommandItem>
            <Calculator className="mr-2 h-4 w-4" /> Calculator
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Settings">
          <CommandItem>
            <User className="mr-2 h-4 w-4" /> Profile
            <CommandShortcut>⌘P</CommandShortcut>
          </CommandItem>
          <CommandItem>
            <Settings className="mr-2 h-4 w-4" /> Settings
            <CommandShortcut>⌘,</CommandShortcut>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </Command>
  ),
};

function DialogDemo() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button onClick={() => setOpen(true)}>Open Command Palette</Button>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Type a command or search…" />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup heading="Suggestions">
            <CommandItem onSelect={() => setOpen(false)}>
              <Calendar className="mr-2 h-4 w-4" /> Calendar
            </CommandItem>
            <CommandItem onSelect={() => setOpen(false)}>
              <Smile className="mr-2 h-4 w-4" /> Search emoji
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  );
}

export const Dialog: Story = { render: () => <DialogDemo /> };

export const Simple: Story = {
  render: () => (
    <Command className="w-80 rounded-lg border">
      <CommandInput placeholder="Search…" />
      <CommandList>
        <CommandEmpty>No results.</CommandEmpty>
        <CommandGroup>
          <CommandItem>Item 1</CommandItem>
          <CommandItem>Item 2</CommandItem>
          <CommandItem>Item 3</CommandItem>
        </CommandGroup>
      </CommandList>
    </Command>
  ),
};
