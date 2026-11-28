import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
  Popover,
  PopoverContent,
  PopoverTrigger,
  ResponsiveSheet,
  ResponsiveSheetContent,
  ResponsiveSheetDescription,
  ResponsiveSheetFooter,
  ResponsiveSheetHeader,
  ResponsiveSheetTitle,
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SidePanel,
  SidePanelBody,
  SidePanelClose,
  SidePanelContent,
  SidePanelDescription,
  SidePanelHeader,
  SidePanelTitle,
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Overlay/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Every overlay in `ui-core`, side by side. They all render on top of the page, ' +
          'so the question is never *what* but *which*: pick along two axes — ' +
          '**does it block the page** (modal vs non-modal), and ' +
          '**does it demand an answer** (a decision, a task, or just more information). ' +
          'Each cell holds its own trigger, so the page is a working menu you can click through. ' +
          '`TooltipProvider` and `DialogProvider` are mounted by the Storybook preview; ' +
          'never nest another one inside a story.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

function DialogCell() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit profile</DialogTitle>
          <DialogDescription>A focused task, dismissible without answering.</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="ghost">Cancel</Button>
          </DialogClose>
          <Button>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function AlertDialogCell() {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="outline">Open AlertDialog</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete this project?</AlertDialogTitle>
          <AlertDialogDescription>
            This cannot be undone. Escape and outside-click are deliberately not enough.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction>Delete</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

function SheetCell() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline">Open Sheet</Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Filters</SheetTitle>
          <SheetDescription>Edge-anchored panel, full height.</SheetDescription>
        </SheetHeader>
        <SheetFooter>
          <SheetClose asChild>
            <Button>Apply</Button>
          </SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}

function DrawerCell() {
  return (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="outline">Open Drawer</Button>
      </DrawerTrigger>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Share</DrawerTitle>
          <DrawerDescription>Bottom sheet with drag-to-dismiss.</DrawerDescription>
        </DrawerHeader>
        <DrawerFooter>
          <DrawerClose asChild>
            <Button variant="outline">Close</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}

/** No Trigger subcomponent — controlled by `open` from an external button. */
function ResponsiveSheetCell() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open ResponsiveSheet
      </Button>
      <ResponsiveSheet open={open} onOpenChange={setOpen}>
        <ResponsiveSheetContent className="sm:max-w-md">
          <ResponsiveSheetHeader>
            <ResponsiveSheetTitle>Edit profile</ResponsiveSheetTitle>
            <ResponsiveSheetDescription>
              Dialog on desktop, Drawer under 768px. Resize to flip it.
            </ResponsiveSheetDescription>
          </ResponsiveSheetHeader>
          <ResponsiveSheetFooter>
            <Button onClick={() => setOpen(false)}>Done</Button>
          </ResponsiveSheetFooter>
        </ResponsiveSheetContent>
      </ResponsiveSheet>
    </>
  );
}

/** Non-modal: the trigger stays clickable while the panel is open. */
function SidePanelCell() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open SidePanel
      </Button>
      <SidePanel open={open} onOpenChange={setOpen} side="right">
        <SidePanelContent>
          <SidePanelHeader>
            <SidePanelTitle>Inspector</SidePanelTitle>
            <SidePanelClose className="ml-auto" />
          </SidePanelHeader>
          <SidePanelBody>
            <div className="space-y-2 p-4 text-sm">
              <SidePanelDescription>
                The page behind stays interactive — try the trigger again.
              </SidePanelDescription>
            </div>
          </SidePanelBody>
        </SidePanelContent>
      </SidePanel>
    </>
  );
}

function PopoverCell() {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline">Open Popover</Button>
      </PopoverTrigger>
      <PopoverContent className="w-64">
        <p className="text-sm">Anchored, focusable, holds real controls.</p>
      </PopoverContent>
    </Popover>
  );
}

function HoverCardCell() {
  return (
    <HoverCard>
      <HoverCardTrigger asChild>
        <Button variant="outline">Hover for HoverCard</Button>
      </HoverCardTrigger>
      <HoverCardContent className="w-64">
        <p className="text-sm">Preview of the thing behind the link. Never load-bearing.</p>
      </HoverCardContent>
    </HoverCard>
  );
}

function TooltipCell() {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant="outline">Hover for Tooltip</Button>
      </TooltipTrigger>
      <TooltipContent>Names the control. One line, no controls.</TooltipContent>
    </Tooltip>
  );
}

/**
 * The whole group on one screen.
 *
 * Grouped by what the overlay does to the page — blocks it, docks beside it,
 * or floats over it — rather than alphabetically, which files `Drawer` next to
 * `HoverCard` and hides the only distinction that matters.
 */
export const AllOverlays: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="Modal — blocks the page">
        <Gallery>
          <GalleryItem name="Dialog" hint="Centered task; escape closes it.">
            <DialogCell />
          </GalleryItem>
          <GalleryItem name="AlertDialog" hint="Destructive confirm; demands an answer.">
            <AlertDialogCell />
          </GalleryItem>
          <GalleryItem name="Sheet" hint="Edge panel for longer forms.">
            <SheetCell />
          </GalleryItem>
          <GalleryItem name="Drawer" hint="Bottom sheet, drag to dismiss.">
            <DrawerCell />
          </GalleryItem>
          <GalleryItem name="ResponsiveSheet" hint="Dialog on desktop, Drawer on mobile.">
            <ResponsiveSheetCell />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Non-modal — page stays usable">
        <Gallery>
          <GalleryItem name="SidePanel" hint="Docked inspector; page keeps working.">
            <SidePanelCell />
          </GalleryItem>
          <GalleryItem name="Popover" hint="Anchored panel with real controls.">
            <PopoverCell />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Transient — hover only, read-only">
        <Gallery>
          <GalleryItem name="HoverCard" hint="Rich preview of a link target.">
            <HoverCardCell />
          </GalleryItem>
          <GalleryItem name="Tooltip" hint="One line naming an icon button.">
            <TooltipCell />
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};
