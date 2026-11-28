import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Button,
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Overlay/Sheet',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

const sides = ['top', 'right', 'bottom', 'left'] as const;

export const Right: Story = {
  render: () => (
    <Sheet>
      <SheetTrigger asChild>
        <Button>Open from right</Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Edit profile</SheetTitle>
          <SheetDescription>
            Make changes to your profile. Click save when done.
          </SheetDescription>
        </SheetHeader>
        <p className="px-4 py-2 text-sm text-muted-foreground">
          (form content here)
        </p>
        <SheetFooter>
          <SheetClose asChild>
            <Button>Save</Button>
          </SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  ),
};

export const Left: Story = {
  render: () => (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline">Open Left</Button>
      </SheetTrigger>
      <SheetContent side="left">
        <SheetHeader>
          <SheetTitle>Navigation</SheetTitle>
        </SheetHeader>
        <nav className="flex flex-col gap-2 py-4">
          {['Dashboard', 'Projects', 'Settings', 'Help'].map((l) => (
            <Button key={l} variant="ghost" className="justify-start">
              {l}
            </Button>
          ))}
        </nav>
      </SheetContent>
    </Sheet>
  ),
};

export const Bottom: Story = {
  render: () => (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline">Open Bottom</Button>
      </SheetTrigger>
      <SheetContent side="bottom">
        <SheetHeader>
          <SheetTitle>Quick Actions</SheetTitle>
          <SheetDescription>Choose an action to perform.</SheetDescription>
        </SheetHeader>
        <div className="flex gap-2 py-4">
          <Button className="flex-1">Share</Button>
          <Button className="flex-1" variant="outline">
            Copy Link
          </Button>
          <Button className="flex-1" variant="destructive">
            Delete
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  ),
};

export const Top: Story = {
  render: () => (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline">Open Top</Button>
      </SheetTrigger>
      <SheetContent side="top">
        <SheetHeader>
          <SheetTitle>Notification</SheetTitle>
          <SheetDescription>You have new updates available.</SheetDescription>
        </SheetHeader>
        <div className="flex gap-2 py-4">
          <Button>Update Now</Button>
          <SheetClose asChild>
            <Button variant="outline">Later</Button>
          </SheetClose>
        </div>
      </SheetContent>
    </Sheet>
  ),
};

export const AllSides: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      {sides.map((side) => (
        <Sheet key={side}>
          <SheetTrigger asChild>
            <Button variant="outline">{side}</Button>
          </SheetTrigger>
          <SheetContent side={side}>
            <SheetHeader>
              <SheetTitle>Side: {side}</SheetTitle>
            </SheetHeader>
            <p className="px-4 py-2 text-sm">Drawer body.</p>
          </SheetContent>
        </Sheet>
      ))}
    </div>
  ),
};
