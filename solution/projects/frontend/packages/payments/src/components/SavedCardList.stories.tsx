import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { SavedCardList, type SavedCard, type SavedCardsPhase } from '@djangocfg/payments';

/**
 * Cards on file. The host feeds `phase` from `useSavedCards`; these stories
 * pass each phase directly so every state is reachable without a backend.
 *
 * The four phases are the point. `unavailable` (the adapter defines no card
 * methods), `loading` (never read), `ready` (possibly empty) and `error` (with
 * the last known list) render differently on purpose — collapsing them into an
 * empty table tells a host that never wired the endpoints that its customer
 * has no card.
 */
const meta: Meta<typeof SavedCardList> = {
  title: 'Packages/Payments/SavedCardList',
  component: SavedCardList,
  tags: ['autodocs'],
  argTypes: {
    phase: { table: { disable: true } },
    onAddCard: { table: { disable: true } },
    onSetDefault: { table: { disable: true } },
    onRemove: { table: { disable: true } },
    labels: { table: { disable: true } },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

// Fixed dates, not `new Date()`: the expiry badges are derived from a clock, so
// a relative fixture would change what the story shows from one month to the next.
const NOW = new Date('2026-09-20T00:00:00Z');
const CARDS: SavedCard[] = [
  { id: 'pm_visa', brand: 'visa', last4: '4242', expMonth: 8, expYear: 2029, isDefault: true },
  { id: 'pm_amex', brand: 'amex', last4: '0005', expMonth: 11, expYear: 2026, isDefault: false },
  { id: 'pm_mc', brand: 'mastercard', last4: '4444', expMonth: 3, expYear: 2026, isDefault: false },
];

const ready = (cards: SavedCard[]): SavedCardsPhase => ({
  kind: 'ready',
  cards,
  refreshing: false,
});

/** Default card, one expiring inside the warning window, one already expired. */
export const Default: Story = {
  args: {
    phase: ready(CARDS),
    onAddCard: () => {},
    onSetDefault: () => {},
    onRemove: () => {},
  },
  parameters: {
    docs: {
      description: {
        story: `Rendered against ${NOW.toISOString().slice(0, 10)}: the Amex falls inside the 60-day warning window, the Mastercard is already past its expiry month.`,
      },
    },
  },
};

/** A real customer with no card yet — distinct from "not supported". */
export const Empty: Story = {
  args: { phase: ready([]), onAddCard: () => {} },
};

/** Never loaded. A reserved-height skeleton, so the table cannot reflow. */
export const Loading: Story = {
  args: { phase: { kind: 'loading' } },
};

/** The adapter defines no card methods. No table, no dead "Add card" button. */
export const Unavailable: Story = {
  args: { phase: { kind: 'unavailable' } },
};

/** A failed refresh keeps the last known list rather than blanking it. */
export const ErrorWithPreviousCards: Story = {
  args: {
    phase: { kind: 'error', message: 'Could not reach the billing service.', previous: CARDS },
    onAddCard: () => {},
    onSetDefault: () => {},
    onRemove: () => {},
  },
};

/** The only card cannot be detached — disabled with a reason, never hidden. */
export const SingleCardCannotBeRemoved: Story = {
  args: {
    phase: ready([CARDS[0]!]),
    onAddCard: () => {},
    onRemove: () => {},
  },
};

/** A write in flight: every action is inert until the re-read confirms it. */
export const Busy: Story = {
  args: {
    phase: { kind: 'ready', cards: CARDS, refreshing: true },
    busy: true,
    onAddCard: () => {},
    onSetDefault: () => {},
    onRemove: () => {},
  },
};

/** Read-only: omit the action callbacks and the column disappears with them. */
export const ReadOnly: Story = {
  args: { phase: ready(CARDS) },
};

/** Host-supplied words — the package ships no locale. */
function LocalisedDemo() {
  const [cards] = useState(CARDS);
  return (
    <SavedCardList
      phase={ready(cards)}
      onAddCard={() => {}}
      onRemove={() => {}}
      labels={{
        card: 'Karte',
        expires: 'Gültig bis',
        addCard: 'Karte hinzufügen',
        remove: 'Entfernen',
        defaultBadge: 'Standard',
        expiringSoon: 'Läuft bald ab',
        expired: 'Abgelaufen',
      }}
    />
  );
}

export const Localised: Story = {
  render: () => <LocalisedDemo />,
};
