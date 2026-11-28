import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Button,
  Input,
  Label,
  ResponsiveSheet,
  ResponsiveSheetContent,
  ResponsiveSheetDescription,
  ResponsiveSheetFooter,
  ResponsiveSheetHeader,
  ResponsiveSheetTitle,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Overlay/ResponsiveSheet',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

/**
 * Story bodies live in components, not in `render`.
 *
 * `render` is a plain callback with no identity of its own in React, so hooks
 * called there belong to whatever tree Storybook happens to mount and their
 * state survives or resets in ways nothing here controls. That is what
 * `react-hooks/rules-of-hooks` is flagging.
 */
function DefaultDemo() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button onClick={() => setOpen(true)}>Edit profile</Button>
      <ResponsiveSheet open={open} onOpenChange={setOpen}>
        <ResponsiveSheetContent className="sm:max-w-md">
          <ResponsiveSheetHeader>
            <ResponsiveSheetTitle>Edit profile</ResponsiveSheetTitle>
            <ResponsiveSheetDescription>
              Renders as a Dialog at ≥sm breakpoints and as a bottom Drawer
              on smaller viewports.
            </ResponsiveSheetDescription>
          </ResponsiveSheetHeader>
          <div className="space-y-3 p-4">
            <div className="space-y-1.5">
              <Label htmlFor="rs-name">Name</Label>
              <Input id="rs-name" defaultValue="Mark" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="rs-email">Email</Label>
              <Input id="rs-email" type="email" defaultValue="mark@example.com" />
            </div>
          </div>
          <ResponsiveSheetFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setOpen(false)}>Save</Button>
          </ResponsiveSheetFooter>
        </ResponsiveSheetContent>
      </ResponsiveSheet>
    </>
  );
}

export const Default: Story = {
  render: () => <DefaultDemo />,
};

function ResizeNoteDemo() {
  const [open, setOpen] = useState(false);
  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        Resize the viewport below 768px to see the bottom-sheet variant.
        Above 768px you get a centered Dialog.
      </p>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open responsive sheet
      </Button>
      <ResponsiveSheet open={open} onOpenChange={setOpen}>
        <ResponsiveSheetContent>
          <ResponsiveSheetHeader>
            <ResponsiveSheetTitle>Responsive behaviour</ResponsiveSheetTitle>
            <ResponsiveSheetDescription>
              On desktop you should see a centered modal dialog. On mobile
              the same content slides up from the bottom edge.
            </ResponsiveSheetDescription>
          </ResponsiveSheetHeader>
          <div className="p-4 text-sm">
            No layout changes are required from callers — render the same
            tree, ResponsiveSheet picks the right primitive at runtime via
            <code> useIsMobile</code>.
          </div>
          <ResponsiveSheetFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Close
            </Button>
          </ResponsiveSheetFooter>
        </ResponsiveSheetContent>
      </ResponsiveSheet>
    </div>
  );
}

export const ResizeNote: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'ResponsiveSheet swaps presentation based on viewport width — Dialog ' +
          '(centered modal) on desktop, Drawer (bottom sheet) on mobile (< 768px). ' +
          'Resize the browser, or use Storybook viewport addon presets, to flip ' +
          'between the two. The trigger, controlled `open` state, and content ' +
          'tree stay identical — only the chrome (header padding, close affordance, ' +
          'animation origin) changes.',
      },
    },
  },
  render: () => <ResizeNoteDemo />,
};
