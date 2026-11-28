import { useEffect, useRef, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Button, Portal } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Specialized/Portal',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Renders children into another DOM node (default: document.body), escaping local stacking contexts.',
      },
    },
  },
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
    <div className="space-y-3">
      <p className="text-muted-foreground text-sm">
        The badge below is portaled to <code>document.body</code> — open
        DevTools to confirm.
      </p>
      <Button onClick={() => setOpen((v) => !v)}>
        {open ? 'Hide' : 'Show'} portal child
      </Button>
      {open && (
        <Portal>
          <div className="bg-primary text-primary-foreground fixed right-4 top-4 z-50 rounded-md px-3 py-2 text-sm shadow-lg">
            Rendered into document.body
          </div>
        </Portal>
      )}
    </div>
  );
}

export const Default: Story = {
  render: () => <DefaultDemo />,
};

function CustomContainerDemo() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [mounted, setMounted] = useState(false);

  // ensure target div exists before <Portal/> resolves its container
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="space-y-3">
      <p className="text-muted-foreground text-sm">
        Children rendered into the dashed box below via{' '}
        <code>container</code> prop.
      </p>
      <div
        ref={containerRef}
        className="border-muted-foreground/40 flex min-h-24 items-center justify-center rounded-md border border-dashed p-4"
      >
        <span className="text-muted-foreground text-xs">
          (target container)
        </span>
      </div>
      {mounted && (
        <Portal container={() => containerRef.current}>
          <div className="bg-secondary text-secondary-foreground rounded-md px-3 py-1.5 text-sm">
            Hello from Portal!
          </div>
        </Portal>
      )}
    </div>
  );
}

export const CustomContainer: Story = {
  render: () => <CustomContainerDemo />,
};

export const DisablePortal: Story = {
  render: () => (
    <div className="space-y-3">
      <p className="text-muted-foreground text-sm">
        With <code>disablePortal</code>, children render in-place (no
        teleport).
      </p>
      <div className="rounded-md border p-4">
        <Portal disablePortal>
          <span className="bg-muted rounded px-2 py-0.5 text-sm">
            In-place child
          </span>
        </Portal>
      </div>
    </div>
  ),
};
