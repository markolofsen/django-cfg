import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Button,
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Overlay/Drawer',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="outline">Open drawer</Button>
      </DrawerTrigger>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Edit profile</DrawerTitle>
          <DrawerDescription>
            Bottom sheet on touch devices. Pull down or tap outside to close.
          </DrawerDescription>
        </DrawerHeader>
        <div className="p-4 text-sm text-muted-foreground">
          Drawer body content lives here. Replace with whatever form, list, or
          action menu you need.
        </div>
        <DrawerFooter>
          <Button>Save</Button>
          <DrawerClose asChild>
            <Button variant="outline">Cancel</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  ),
};

/**
 * Story bodies live in components, not in `render`.
 *
 * `render` is a plain callback with no identity of its own in React, so hooks
 * called there belong to whatever tree Storybook happens to mount and their
 * state survives or resets in ways nothing here controls. That is what
 * `react-hooks/rules-of-hooks` is flagging.
 */
function NonModalDemo() {
  const [open, setOpen] = useState(false);
  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        With <code>modal={'{false}'}</code> the rest of the page stays
        interactive while the drawer is open — useful for inspectors and
        help panels.
      </p>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open non-modal drawer
      </Button>
      <Drawer open={open} onOpenChange={setOpen} modal={false}>
        <DrawerContent>
          <DrawerHeader>
            <DrawerTitle>Non-modal drawer</DrawerTitle>
            <DrawerDescription>
              Click outside — the page below still receives events.
            </DrawerDescription>
          </DrawerHeader>
          <div className="p-4 text-sm">
            Try clicking the &ldquo;Open non-modal drawer&rdquo; button again
            while this is open.
          </div>
          <DrawerFooter>
            <DrawerClose asChild>
              <Button variant="outline">Close</Button>
            </DrawerClose>
          </DrawerFooter>
        </DrawerContent>
      </Drawer>
    </div>
  );
}

export const NonModal: Story = {
  render: () => <NonModalDemo />,
};

function SnapDemo() {
  const [snap, setSnap] = useState<number | string | null>(0.4);
  return (
    <Drawer snapPoints={[0.4, 0.75, 1]} activeSnapPoint={snap} setActiveSnapPoint={setSnap}>
      <DrawerTrigger asChild>
        <Button variant="outline">Open snap drawer</Button>
      </DrawerTrigger>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Snap points</DrawerTitle>
          <DrawerDescription>
            Drag the handle to snap between 40%, 75%, and 100% of viewport
            height. Current snap: <code>{String(snap)}</code>.
          </DrawerDescription>
        </DrawerHeader>
        <div className="p-4 space-y-2 text-sm">
          <p>This pattern is common for map filters, audio queues, and
          mobile media controls.</p>
          <p className="text-muted-foreground">
            Snap state is controlled — wire <code>activeSnapPoint</code> and
            <code> setActiveSnapPoint</code> to remember the user&rsquo;s
            preferred height across sessions.
          </p>
        </div>
        <DrawerFooter>
          <DrawerClose asChild>
            <Button variant="outline">Close</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}

export const Snap: Story = {
  render: () => <SnapDemo />,
};

export const LongContent: Story = {
  render: () => (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="outline">Open long drawer</Button>
      </DrawerTrigger>
      <DrawerContent className="max-h-[85vh]">
        <DrawerHeader>
          <DrawerTitle>Changelog</DrawerTitle>
          <DrawerDescription>
            Long content scrolls inside the drawer body.
          </DrawerDescription>
        </DrawerHeader>
        <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-3 text-sm">
          {Array.from({ length: 30 }).map((_, i) => (
            <div key={i} className="rounded border p-3">
              <div className="font-medium">Entry #{i + 1}</div>
              <p className="text-muted-foreground">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua.
              </p>
            </div>
          ))}
        </div>
        <DrawerFooter>
          <DrawerClose asChild>
            <Button variant="outline">Close</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  ),
};

/* ---------------------------------------------------------------------------
 * A form taller than the sheet it opens in
 * ------------------------------------------------------------------------ */

/**
 * The case a catalogue's mobile filters actually hit: the sheet opens at half
 * height, the form continues past the bottom edge, and the reader wants it
 * TALLER — not closed.
 *
 * Without snap points a bottom drawer has exactly two positions, open and
 * closed, so the only gesture it answers is a downward one. Dragging up has
 * nowhere to go. Snap points give it the intermediate state that the upward
 * drag needs, and the same gesture that closes the sheet also expands it.
 *
 * What to check: open, drag the handle UP — the sheet grows to 92% and the
 * fields below the fold come into view; drag DOWN — it returns to half, and
 * again to dismiss. Fields stay usable at both heights.
 */
function ExpandableFormDemo() {
  const [snap, setSnap] = useState<number | string | null>(0.5);
  return (
    <Drawer snapPoints={[0.5, 0.92]} activeSnapPoint={snap} setActiveSnapPoint={setSnap}>
      <DrawerTrigger asChild>
        <Button variant="outline">Filters</Button>
      </DrawerTrigger>
      <DrawerContent>
        <DrawerHeader className="border-b border-border">
          <DrawerTitle>Filters</DrawerTitle>
          <DrawerDescription>
            Drag the handle up to expand. Snap: <code>{String(snap)}</code>
          </DrawerDescription>
        </DrawerHeader>
        <div className="space-y-4 py-4">
          {['Brand', 'Body type', 'Fuel', 'Transmission', 'Year', 'Mileage', 'Colour', 'Seats'].map(
            (field) => (
              <label key={field} className="block space-y-1.5">
                <span className="text-sm font-medium">{field}</span>
                <select className="h-10 w-full rounded-[var(--radius)] border border-border bg-input px-3 text-sm">
                  <option>Any</option>
                </select>
              </label>
            ),
          )}
        </div>
        <DrawerFooter>
          <DrawerClose asChild>
            <Button>Show results</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}

export const ExpandableForm: Story = {
  parameters: {
    viewport: { defaultViewport: 'mobile1' },
    docs: {
      description: {
        story:
          'A form taller than the sheet. Opens at half height and drags UP to expand — the gesture a plain bottom drawer cannot answer.',
      },
    },
  },
  render: () => <ExpandableFormDemo />,
};
