import { useRef, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, userEvent, waitFor, within } from 'storybook/test';
import { Button } from '@djangocfg/ui-core';
import {
  CheckoutDialog,
  CheckoutForm,
  PaymentProvider,
  createMockPaymentAdapter,
  type MockOutcome,
} from '@djangocfg/payments';

/**
 * The dialog shell every checkout host needs: CheckoutGuardProvider + a
 * close-locked ui-core Dialog. Open it, press Pay, and try to close while the
 * payment is processing — Esc, overlay-click and the × are all disabled until
 * the charge reaches a terminal state (the inner CheckoutForm publishes its
 * status into the guard automatically). The body scrolls inside the dialog so
 * a tall Stripe form never clips.
 */
const meta: Meta<typeof CheckoutDialog> = {
  title: 'Packages/Payments/CheckoutDialog',
  component: CheckoutDialog,
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
  argTypes: {
    open: { table: { disable: true } },
    onClose: { table: { disable: true } },
    children: { table: { disable: true } },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

/** Interactive host: a launcher button + the dialog with a mock checkout. */
function DialogDemo({
  outcome,
  title,
  latencyMs,
}: {
  outcome: MockOutcome;
  title?: string;
  latencyMs?: number;
}) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const closeAndRestoreFocus = () => {
    setOpen(false);
    requestAnimationFrame(() => triggerRef.current?.focus());
  };

  return (
    <PaymentProvider adapter={createMockPaymentAdapter({ outcome, latencyMs })}>
      <Button ref={triggerRef} onClick={() => setOpen(true)}>Open checkout</Button>
      <CheckoutDialog open={open} onClose={closeAndRestoreFocus} title={title}>
        <CheckoutForm
          amount={2900}
          currency="usd"
          reference={{ kind: 'order', id: 'ord_demo' }}
          summaryTitle="Pro plan"
          summaryNote="Billed monthly"
          isMock
          onSuccess={closeAndRestoreFocus}
          onCancel={closeAndRestoreFocus}
        />
      </CheckoutDialog>
    </PaymentProvider>
  );
}

/** Pay succeeds — dialog closes itself via onSuccess. */
export const Success: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  render: () => <DialogDemo outcome="succeeded" latencyMs={10} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button', { name: 'Open checkout' });

    await userEvent.click(trigger);

    const dialog = within(document.body).getByRole('dialog', { name: 'Checkout' });
    await expect(within(dialog).getByText('Pro plan')).toBeInTheDocument();
    await userEvent.click(within(dialog).getByRole('button', { name: 'Pay $29.00' }));

    await waitFor(() => expect(dialog).not.toBeInTheDocument(), { timeout: 3_000 });
    await expect(trigger).toHaveFocus();
  },
};

/**
 * 3DS challenge — the checkout parks in `requires_action`, and the dialog
 * stays LOCKED: no Esc, no overlay-click, no × until the state resolves.
 */
export const LockedWhileRequiresAction: Story = {
  render: () => <DialogDemo outcome="requires_action" title="Secure checkout" />,
};

/** Declined — terminal `failed` unlocks the dialog again (error stays visible). */
export const Declined: Story = {
  render: () => <DialogDemo outcome="failed" />,
};
