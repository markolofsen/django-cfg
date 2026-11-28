// ============================================================================
// @djangocfg/payments — card derivations (pure: no React, no Stripe)
// ============================================================================
// `SavedCard` stores only what the provider states. Everything below is
// derived against a clock, so it lives here rather than in a component: two
// readers computing "expiring soon" separately drift the first time one of
// them forgets that a card is valid through the END of its expiry month.

import type { SavedCard, SavedCardsPhase } from './types';

/** The cards a phase carries. `error` keeps the last known list, so it renders. */
export function cardsOf(phase: SavedCardsPhase): SavedCard[] {
  if (phase.kind === 'ready') return phase.cards;
  if (phase.kind === 'error') return phase.previous ?? [];
  return [];
}

/** Days before expiry at which a card is worth flagging. */
export const EXPIRY_WARNING_DAYS = 60;

/**
 * The instant a card stops working: midnight after the last day of its expiry
 * month. A card marked 08/2026 is valid through 2026-08-31.
 */
export function cardExpiresAt(card: SavedCard): Date {
  // Day 1 of the FOLLOWING month. `Date` normalizes month 12 into next
  // January, so December needs no special case.
  return new Date(card.expYear, card.expMonth, 1);
}

/** Whether the card can no longer be charged. */
export function isCardExpired(card: SavedCard, now: Date = new Date()): boolean {
  return cardExpiresAt(card).getTime() <= now.getTime();
}

/**
 * Whether the card still works but is close enough to expiry to warn about.
 * False for an already-expired card — that is a different, louder state.
 */
export function isCardExpiringSoon(
  card: SavedCard,
  now: Date = new Date(),
  withinDays: number = EXPIRY_WARNING_DAYS,
): boolean {
  const expiresAt = cardExpiresAt(card).getTime();
  if (expiresAt <= now.getTime()) return false;
  return expiresAt - now.getTime() <= withinDays * 24 * 60 * 60 * 1000;
}

/** `expMonth`/`expYear` as `MM/YY`. Display only. */
export function formatCardExpiry(card: SavedCard): string {
  const month = String(card.expMonth).padStart(2, '0');
  const year = String(card.expYear).slice(-2);
  return `${month}/${year}`;
}

/** Default first, then soonest to expire — the order a chooser wants. */
export function sortCards(cards: readonly SavedCard[]): SavedCard[] {
  return cards.slice().sort((a, b) => {
    if (a.isDefault !== b.isDefault) return a.isDefault ? -1 : 1;
    return cardExpiresAt(a).getTime() - cardExpiresAt(b).getTime();
  });
}
