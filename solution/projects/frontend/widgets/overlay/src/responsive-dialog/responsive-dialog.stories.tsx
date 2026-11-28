import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Button } from '@djangocfg/ui-core/components';
import {
  ResponsiveDialog,
  ResponsiveDialogContent,
  ResponsiveDialogHeader,
  ResponsiveDialogTitle,
  ResponsiveDialogDescription,
  ResponsiveDialogFooter,
} from '.';

const meta = {
  title: 'Widgets/Overlay/ResponsiveDialog',
  component: ResponsiveDialog,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A dialog that automatically switches to a drawer on mobile viewports.',
      },
    },
  },
  args: {
    open: false,
    onOpenChange: () => {},
    children: null,
  },
} satisfies Meta<typeof ResponsiveDialog>;

export default meta;
type Story = StoryObj<typeof meta>;

function DialogHost() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button onClick={() => setOpen(true)}>Open Dialog</Button>
      <ResponsiveDialog open={open} onOpenChange={setOpen}>
        <ResponsiveDialogContent>
          <ResponsiveDialogHeader>
            <ResponsiveDialogTitle>Confirm Action</ResponsiveDialogTitle>
            <ResponsiveDialogDescription>
              This dialog becomes a drawer on mobile. Resize the viewport to see the switch.
            </ResponsiveDialogDescription>
          </ResponsiveDialogHeader>
          <div className="py-4">
            <p className="text-sm text-muted-foreground">
              Content goes here. The component uses `useIsMobile` to decide between Dialog and Drawer.
            </p>
          </div>
          <ResponsiveDialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setOpen(false)}>Confirm</Button>
          </ResponsiveDialogFooter>
        </ResponsiveDialogContent>
      </ResponsiveDialog>
    </>
  );
}

export const Default: Story = {
  render: () => <DialogHost />,
};
