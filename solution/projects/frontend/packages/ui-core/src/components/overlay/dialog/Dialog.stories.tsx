import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, userEvent, waitFor, within } from 'storybook/test';
import {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Input,
  Label,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Overlay/Dialog',
  tags: ['autodocs', 'contract'],
  parameters: { a11y: { test: 'error' } },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit profile</DialogTitle>
          <DialogDescription>
            Update your display name. Changes are saved when you submit.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-3 py-2">
          <div className="grid gap-1.5">
            <Label htmlFor="name">Name</Label>
            <Input id="name" defaultValue="Mark" />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="handle">Handle</Label>
            <Input id="handle" defaultValue="@markolofsen" />
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="ghost">Cancel</Button>
          </DialogClose>
          <Button>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button', { name: 'Open dialog' });

    await userEvent.click(trigger);

    const dialog = within(document.body).getByRole('dialog', {
      name: 'Edit profile',
    });
    await expect(within(dialog).getByLabelText('Name')).toHaveFocus();

    await userEvent.click(within(dialog).getByRole('button', { name: 'Cancel' }));
    await waitFor(() => expect(dialog).not.toBeInTheDocument());
    await expect(trigger).toHaveFocus();
  },
};

export const Destructive: Story = {
  // Shared destructive token is 3.65:1 in the current macOS preset.
  parameters: { a11y: { test: 'todo' } },
  render: () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="destructive">Delete account</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Are you sure?</DialogTitle>
          <DialogDescription>
            This permanently deletes your account and all associated data.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="ghost">Cancel</Button>
          </DialogClose>
          <Button variant="destructive">Yes, delete</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  ),
};

export const Fullscreen: Story = {
  render: () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Open fullscreen dialog</Button>
      </DialogTrigger>
      <DialogContent fullscreen>
        <div className="mx-auto flex h-full w-full max-w-3xl flex-col px-4 py-10 sm:px-6 lg:px-8">
          <DialogTitle className="text-2xl font-semibold tracking-tight">
            Fullscreen layout
          </DialogTitle>
          <DialogDescription className="mt-1 text-muted-foreground">
            `fullscreen` stretches content to the viewport.
          </DialogDescription>
          <div className="mt-6 flex-1 rounded-xl border border-dashed bg-muted/30 p-6 text-sm text-muted-foreground">
            Slot for a custom layout — gallery, onboarding, command palette, etc.
          </div>
        </div>
      </DialogContent>
    </Dialog>
  ),
};

export const NoCloseButton: Story = {
  render: () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Modal step (no close)</Button>
      </DialogTrigger>
      <DialogContent closeButton={false}>
        <DialogHeader>
          <DialogTitle>Saving…</DialogTitle>
          <DialogDescription>
            The dialog has no close affordance — dismiss via action buttons.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Back</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  ),
};

export const LongContent: Story = {
  render: () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Terms of Service</Button>
      </DialogTrigger>
      <DialogContent className="max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Terms of Service</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4 text-sm text-muted-foreground">
          {Array.from({ length: 4 }).map((_, i) => (
            <p key={i}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </p>
          ))}
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Decline</Button>
          </DialogClose>
          <Button>Accept</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  ),
};
