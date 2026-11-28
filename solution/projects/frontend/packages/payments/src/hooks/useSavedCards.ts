'use client';

// ============================================================================
// @djangocfg/payments — useSavedCards
// ============================================================================
// Owns the cards-on-file list via the adapter's optional listPaymentMethods().
//
// WHY A PHASE AND NOT A BOOLEAN PAIR. `[]` answers three different questions
// identically: the host never wired the endpoint, the request has not run yet,
// and the customer genuinely has no card. The first renders a dead "Add card"
// button, the second flashes an empty table before data lands, the third is a
// real empty state. They are different screens, so they are different states.

import { useCallback, useEffect, useState } from 'react';
import { usePaymentAdapter } from '../context/PaymentProvider';
import type { SavedCard, SavedCardsPhase } from '../domain/types';
import { cardsOf, sortCards } from '../domain/cards';

export interface UseSavedCardsResult {
  phase: SavedCardsPhase;
  /** Cards known right now, including during a refresh or after a failed one. */
  cards: SavedCard[];
  /** Whether the adapter can add a card. Gates the primary action. */
  canAddCard: boolean;
  /** Whether the adapter can change the default and detach a card. */
  canManageCards: boolean;
  refresh: () => Promise<void>;
  /** Make one card the default for renewals, then re-read. */
  setDefault: (id: string) => Promise<void>;
  /** Detach a card, then re-read. Rejects on the last card of an active subscription. */
  remove: (id: string) => Promise<void>;
  /** True while any of the three calls is in flight. */
  isBusy: boolean;
}

export interface UseSavedCardsProps {
  /** Load on mount. Default true. */
  autoLoad?: boolean;
}

export function useSavedCards(
  { autoLoad = true }: UseSavedCardsProps = {},
): UseSavedCardsResult {
  const adapter = usePaymentAdapter();
  const canList = typeof adapter.listPaymentMethods === 'function';
  const canAddCard = typeof adapter.createSetupIntent === 'function';
  const canManageCards =
    typeof adapter.setDefaultPaymentMethod === 'function' &&
    typeof adapter.removePaymentMethod === 'function';

  const [phase, setPhase] = useState<SavedCardsPhase>(
    canList ? { kind: 'loading' } : { kind: 'unavailable' },
  );
  const [isBusy, setIsBusy] = useState(false);

  const refresh = useCallback(async () => {
    if (!adapter.listPaymentMethods) {
      setPhase({ kind: 'unavailable' });
      return;
    }
    setPhase((prev) =>
      prev.kind === 'ready'
        ? { ...prev, refreshing: true }
        : prev.kind === 'error'
          ? { kind: 'loading' }
          : prev,
    );
    try {
      const list = await adapter.listPaymentMethods();
      setPhase({ kind: 'ready', cards: sortCards(list), refreshing: false });
    } catch (e) {
      setPhase((prev) => ({
        kind: 'error',
        message: e instanceof Error ? e.message : 'Failed to load cards.',
        previous: cardsOf(prev),
      }));
    }
  }, [adapter]);

  // A write is only believed once the re-read confirms it: the server may
  // refuse (detaching the last card) or adjust (promoting a new default), and
  // an optimistic list would state the opposite of what renewals will charge.
  const mutate = useCallback(
    async (run: () => Promise<void>, fallback: string) => {
      setIsBusy(true);
      try {
        await run();
        await refresh();
      } catch (e) {
        setPhase((prev) => ({
          kind: 'error',
          message: e instanceof Error ? e.message : fallback,
          previous: cardsOf(prev),
        }));
      } finally {
        setIsBusy(false);
      }
    },
    [refresh],
  );

  const setDefault = useCallback(
    (id: string) =>
      mutate(async () => {
        if (!adapter.setDefaultPaymentMethod) {
          throw new Error('This payment provider cannot change the default card.');
        }
        await adapter.setDefaultPaymentMethod(id);
      }, 'Failed to change the default card.'),
    [adapter, mutate],
  );

  const remove = useCallback(
    (id: string) =>
      mutate(async () => {
        if (!adapter.removePaymentMethod) {
          throw new Error('This payment provider cannot remove a card.');
        }
        await adapter.removePaymentMethod(id);
      }, 'Failed to remove the card.'),
    [adapter, mutate],
  );

  useEffect(() => {
    if (autoLoad && canList) void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoLoad, canList]);

  return {
    phase,
    cards: cardsOf(phase),
    canAddCard,
    canManageCards,
    refresh,
    setDefault,
    remove,
    isBusy,
  };
}
