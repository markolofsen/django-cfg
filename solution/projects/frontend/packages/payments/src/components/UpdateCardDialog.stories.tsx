import { useRef, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, userEvent, waitFor, within } from 'storybook/test';
import { Button } from '@djangocfg/ui-core';
import {
  PaymentProvider,
  SavedCardList,
  UpdateCardDialog,
  createMockPaymentAdapter,
  useSavedCards,
  type MockOutcome,
} from '@djangocfg/payments';

/**
 * Put a card on file. A SetupIntent is created when the dialog OPENS (Stripe's
 * <Elements> needs the client secret before it mounts), confirmed with
 * `confirmSetup`, and nothing is charged.
 *
 * What the success state does and does not mean: Stripe stored the card. It is
 * not proof that a past-due subscription recovered — that arrives by webhook,
 * which is why the dialog says "Card saved" and stops there.
 */
const meta: Meta<typeof UpdateCardDialog> = {
  title: 'Packages/Payments/UpdateCardDialog',
  component: UpdateCardDialog,
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
  argTypes: {
    open: { table: { disable: true } },
    onClose: { table: { disable: true } },
    renderCardStep: { table: { disable: true } },
    onSaved: { table: { disable: true } },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

/** Launcher + dialog on the mock adapter — no Stripe key, no network. */
function DialogDemo({
  outcome,
  latencyMs,
  supportsCards = true,
}: {
  outcome?: MockOutcome;
  latencyMs?: number;
  /** `cards: null` drops the four card methods — the `unavailable` path. */
  supportsCards?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const closeAndRestoreFocus = () => {
    setOpen(false);
    requestAnimationFrame(() => triggerRef.current?.focus());
  };

  const adapter = createMockPaymentAdapter({
    outcome,
    latencyMs,
    ...(supportsCards ? {} : { cards: null }),
  });

  return (
    <PaymentProvider adapter={adapter}>
      <Button ref={triggerRef} onClick={() => setOpen(true)}>
        Add card
      </Button>
      <UpdateCardDialog
        open={open}
        onClose={closeAndRestoreFocus}
        isMock
        onSaved={closeAndRestoreFocus}
      />
    </PaymentProvider>
  );
}

/** The card is stored — the dialog reports "Card saved" and closes. */
export const Success: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  render: () => <DialogDemo outcome="succeeded" latencyMs={10} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button', { name: 'Add card' });

    await userEvent.click(trigger);

    const dialog = await waitFor(() =>
      within(document.body).getByRole('dialog', { name: 'Add a card' }),
    );
    // The consent sentence is not decoration: Stripe infers the off-session
    // mandate from the text on screen, so its absence is a defect.
    await expect(within(dialog).getByText(/authorise us to charge it/i)).toBeInTheDocument();

    const save = await waitFor(() => within(dialog).getByRole('button', { name: 'Save card' }));
    await userEvent.click(save);

    await waitFor(() => expect(dialog).not.toBeInTheDocument(), { timeout: 3_000 });
    await expect(trigger).toHaveFocus();
  },
};

/** Declined — terminal `failed`, the dialog unlocks and the reason stays up. */
export const Declined: Story = {
  render: () => <DialogDemo outcome="failed" />,
};

/**
 * The issuer wants a challenge. The dialog is LOCKED while it runs: closing
 * over a half-confirmed SetupIntent leaves an authorisation nobody resolves.
 */
export const LockedWhileRequiresAction: Story = {
  render: () => <DialogDemo outcome="requires_action" />,
};

/** An adapter with no card methods says so, instead of showing a dead form. */
export const Unavailable: Story = {
  render: () => <DialogDemo supportsCards={false} />,
};

/**
 * The whole surface: the list, the dialog, and the re-read that follows a
 * save. Adding a card here updates the table because `useSavedCards` refreshes
 * from the adapter — nothing is written optimistically.
 */
function BillingSectionDemo() {
  const [open, setOpen] = useState(false);
  const { phase, canAddCard, canManageCards, refresh, setDefault, remove, isBusy } =
    useSavedCards();

  return (
    <div className="w-[36rem] space-y-4">
      <SavedCardList
        phase={phase}
        busy={isBusy}
        onAddCard={canAddCard ? () => setOpen(true) : undefined}
        onSetDefault={canManageCards ? setDefault : undefined}
        onRemove={canManageCards ? remove : undefined}
      />
      <UpdateCardDialog
        open={open}
        onClose={() => setOpen(false)}
        isMock
        onSaved={() => {
          setOpen(false);
          void refresh();
        }}
      />
    </div>
  );
}

export const BillingSection: Story = {
  parameters: { layout: 'padded' },
  render: () => (
    <PaymentProvider adapter={createMockPaymentAdapter({ latencyMs: 200 })}>
      <BillingSectionDemo />
    </PaymentProvider>
  ),
};
