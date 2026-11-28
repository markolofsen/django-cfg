import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Button,
  Combobox,
  SidePanel,
  SidePanelBody,
  SidePanelClose,
  SidePanelContent,
  SidePanelDescription,
  SidePanelFooter,
  SidePanelHeader,
  SidePanelTitle,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Overlay/SidePanel',
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
function RightDemo() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open right panel
      </Button>
      <SidePanel open={open} onOpenChange={setOpen} side="right">
        <SidePanelContent>
          <SidePanelHeader>
            <SidePanelTitle>Inspector</SidePanelTitle>
            <SidePanelClose className="ml-auto" />
          </SidePanelHeader>
          <SidePanelBody>
            <div className="p-4 space-y-2 text-sm">
              <SidePanelDescription>
                Non-modal: the rest of the page stays interactive while the
                panel is open. Press Esc or the close button to dismiss.
              </SidePanelDescription>
              <p className="text-muted-foreground">
                Try clicking the trigger again — the page is not locked.
              </p>
            </div>
          </SidePanelBody>
        </SidePanelContent>
      </SidePanel>
    </>
  );
}

export const Right: Story = {
  render: () => <RightDemo />,
};

function LeftDemo() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open left panel
      </Button>
      <SidePanel open={open} onOpenChange={setOpen} side="left">
        <SidePanelContent>
          <SidePanelHeader>
            <SidePanelTitle>Navigation</SidePanelTitle>
            <SidePanelClose className="ml-auto" />
          </SidePanelHeader>
          <SidePanelBody>
            <nav className="flex flex-col p-2 text-sm">
              {['Inbox', 'Projects', 'Tasks', 'Settings'].map((item) => (
                <button
                  key={item}
                  className="text-left rounded px-3 py-2 hover:bg-muted"
                >
                  {item}
                </button>
              ))}
            </nav>
          </SidePanelBody>
        </SidePanelContent>
      </SidePanel>
    </>
  );
}

export const Left: Story = {
  render: () => <LeftDemo />,
};

function ResizableDemo() {
  const [open, setOpen] = useState(false);
  const [wide, setWide] = useState(false);
  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open resizable panel
      </Button>
      <SidePanel open={open} onOpenChange={setOpen} side="right">
        <SidePanelContent width={wide ? '640px' : '360px'}>
          <SidePanelHeader>
            <SidePanelTitle>Width: {wide ? '640px' : '360px'}</SidePanelTitle>
            <Button
              size="sm"
              variant="outline"
              className="ml-auto"
              onClick={() => setWide((w) => !w)}
            >
              {wide ? 'Compact' : 'Wide'}
            </Button>
            <SidePanelClose />
          </SidePanelHeader>
          <SidePanelBody>
            <div className="p-4 text-sm text-muted-foreground">
              Width transitions are baked into SidePanelContent — swap the
              <code> width</code> prop and the panel animates between sizes.
            </div>
          </SidePanelBody>
        </SidePanelContent>
      </SidePanel>
    </>
  );
}

export const Resizable: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'SidePanel does not ship with a drag handle — pass a `width` to ' +
          'SidePanelContent and animate it via the built-in width transition. ' +
          'This demo toggles between compact (360px) and wide (640px) widths.',
      },
    },
  },
  render: () => <ResizableDemo />,
};

function WithBodyDemo() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open panel with body
      </Button>
      <SidePanel open={open} onOpenChange={setOpen} side="right">
        <SidePanelContent width="480px">
          <SidePanelHeader>
            <SidePanelTitle>Activity log</SidePanelTitle>
            <SidePanelClose className="ml-auto" />
          </SidePanelHeader>
          <SidePanelBody>
            <ul className="divide-y text-sm">
              {Array.from({ length: 25 }).map((_, i) => (
                <li key={i} className="px-4 py-3">
                  <div className="font-medium">Event #{i + 1}</div>
                  <div className="text-muted-foreground">
                    Something happened {i + 1} minute(s) ago.
                  </div>
                </li>
              ))}
            </ul>
          </SidePanelBody>
          <SidePanelFooter>
            <div className="flex justify-end gap-2">
              <SidePanelClose>
                <Button variant="outline" size="sm">
                  Close
                </Button>
              </SidePanelClose>
              <Button size="sm">Mark all read</Button>
            </div>
          </SidePanelFooter>
        </SidePanelContent>
      </SidePanel>
    </>
  );
}

export const WithBody: Story = {
  render: () => <WithBodyDemo />,
};

/* ---------------------------------------------------------------------------
 * Dismissal
 * ------------------------------------------------------------------------ */

const MAKES = ['Volkswagen', 'Toyota', 'Audi', 'Mercedes-Benz', 'Ford'].map(
  (label) => ({ value: label.toLowerCase(), label }),
);

/**
 * A panel with no backdrop still closes on a click outside it.
 *
 * Having no backdrop is a statement about the page — it stays readable,
 * clickable and scrollable — not about the click. With only Esc and a small
 * `×`, a reader who clicked beside the panel got nothing and had to hunt for
 * the button.
 *
 * The case worth checking here is the Combobox: its popover is portalled to
 * `<body>`, so by DOM position it is *outside* the panel. Choosing a make must
 * not dismiss the panel underneath it — and the page behind must still scroll
 * while the panel is open.
 */
function DismissalHost() {
  const [open, setOpen] = useState(false);
  const [make, setMake] = useState('');
  return (
    <div className="h-[150vh] p-6">
      <Button variant="outline" onClick={() => setOpen(true)}>
        Open filters
      </Button>
      <p className="mt-4 max-w-sm text-sm text-muted-foreground">
        The page keeps scrolling while the panel is open. Click anywhere out
        here to dismiss it; pick a make inside and it stays.
      </p>

      <SidePanel open={open} onOpenChange={setOpen}>
        <SidePanelContent>
          <SidePanelHeader>
            <SidePanelTitle>Filters</SidePanelTitle>
            <SidePanelClose className="ml-auto" />
          </SidePanelHeader>
          <SidePanelBody className="space-y-4 p-4">
            <SidePanelDescription>
              Selected: {make || '(none)'}
            </SidePanelDescription>
            <Combobox
              options={MAKES}
              value={make}
              onValueChange={setMake}
              placeholder="Any make"
            />
          </SidePanelBody>
          <SidePanelFooter>
            <Button className="w-full" onClick={() => setOpen(false)}>
              Show results
            </Button>
          </SidePanelFooter>
        </SidePanelContent>
      </SidePanel>
    </div>
  );
}

export const Dismissal: Story = {
  parameters: { layout: 'fullscreen' },
  render: () => <DismissalHost />,
};
