import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  ContextMenu,
  ContextMenuCheckboxItem,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuRadioGroup,
  ContextMenuRadioItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuSub,
  ContextMenuSubContent,
  ContextMenuSubTrigger,
  ContextMenuTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/ContextMenu',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

function Card({ children }: { children?: React.ReactNode }) {
  return (
    <div className="flex h-40 w-72 select-none items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
      {children ?? 'Right-click me'}
    </div>
  );
}

export const Default: Story = {
  render: () => (
    <ContextMenu>
      <ContextMenuTrigger>
        <Card />
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        <ContextMenuItem>
          Back <ContextMenuShortcut>⌘[</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuItem>
          Forward <ContextMenuShortcut>⌘]</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuItem>
          Reload <ContextMenuShortcut>⌘R</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuItem className="text-destructive">Delete</ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  ),
};

export const Nested: Story = {
  render: () => (
    <ContextMenu>
      <ContextMenuTrigger>
        <Card>Right-click for nested menu</Card>
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        <ContextMenuItem>Open</ContextMenuItem>
        <ContextMenuItem>Rename</ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuSub>
          <ContextMenuSubTrigger>Share</ContextMenuSubTrigger>
          <ContextMenuSubContent>
            <ContextMenuItem>Email Link</ContextMenuItem>
            <ContextMenuItem>Copy Link</ContextMenuItem>
            <ContextMenuSeparator />
            <ContextMenuSub>
              <ContextMenuSubTrigger>More…</ContextMenuSubTrigger>
              <ContextMenuSubContent>
                <ContextMenuItem>Slack</ContextMenuItem>
                <ContextMenuItem>Telegram</ContextMenuItem>
              </ContextMenuSubContent>
            </ContextMenuSub>
          </ContextMenuSubContent>
        </ContextMenuSub>
        <ContextMenuSeparator />
        <ContextMenuItem className="text-destructive">Delete</ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  ),
};

function CheckboxDemo() {
  const [flags, setFlags] = useState({ bookmarks: true, urls: false });
  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <Card>Right-click for checkboxes</Card>
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        <ContextMenuLabel>Bookmarks</ContextMenuLabel>
        <ContextMenuSeparator />
        <ContextMenuCheckboxItem
          checked={flags.bookmarks}
          onCheckedChange={(c) => setFlags((s) => ({ ...s, bookmarks: !!c }))}
        >
          Show Bookmarks
        </ContextMenuCheckboxItem>
        <ContextMenuCheckboxItem
          checked={flags.urls}
          onCheckedChange={(c) => setFlags((s) => ({ ...s, urls: !!c }))}
        >
          Show Full URLs
        </ContextMenuCheckboxItem>
      </ContextMenuContent>
    </ContextMenu>
  );
}

export const WithCheckboxes: Story = {
  render: () => <CheckboxDemo />,
};

function RadioDemo() {
  const [person, setPerson] = useState('alice');
  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <Card>Right-click for radio group</Card>
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        <ContextMenuLabel>Assign to</ContextMenuLabel>
        <ContextMenuSeparator />
        <ContextMenuRadioGroup value={person} onValueChange={setPerson}>
          <ContextMenuRadioItem value="alice">Alice</ContextMenuRadioItem>
          <ContextMenuRadioItem value="bob">Bob</ContextMenuRadioItem>
          <ContextMenuRadioItem value="carol">Carol</ContextMenuRadioItem>
        </ContextMenuRadioGroup>
      </ContextMenuContent>
    </ContextMenu>
  );
}

export const WithRadioGroup: Story = {
  render: () => <RadioDemo />,
};
