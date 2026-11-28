'use client';

// ============================================================================
// @djangocfg/payments — SavedCardList
// ============================================================================
// The cards-on-file table. Pure presentational: the host feeds `phase` (from
// useSavedCards) and the action callbacks. ui-core Table, like PaymentHistory
// — no data-grid, since a package may not depend on a widget.
//
// FOUR STATES, NOT TWO. `unavailable` (the adapter has no card methods),
// `loading` (never read), `ready` (possibly empty), `error` (with whatever was
// last known). Collapsing the first three into an empty table shows "no cards
// on file" to a host that simply never wired the endpoints.

import React from 'react';
import {
  Alert,
  AlertDescription,
  Badge,
  Button,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@djangocfg/ui-core';
import { AlertTriangle, CreditCard, Plus } from 'lucide-react';
import type { SavedCard, SavedCardsPhase } from '../domain/types';
import { cardsOf, formatCardExpiry, isCardExpired, isCardExpiringSoon } from '../domain/cards';

export interface SavedCardListProps {
  phase: SavedCardsPhase;
  /** Open the add-card dialog. Omit to hide the action entirely. */
  onAddCard?: () => void;
  /** Make a card the default for renewals. Omit to hide the row action. */
  onSetDefault?: (id: string) => void;
  /** Detach a card. Omit to hide the row action. */
  onRemove?: (id: string) => void;
  /** Disables every action (a write is in flight). */
  busy?: boolean;
  /** Host-supplied words — this package ships no locale. */
  labels?: Partial<SavedCardListLabels>;
  className?: string;
}

export interface SavedCardListLabels {
  card: string;
  expires: string;
  addCard: string;
  setDefault: string;
  remove: string;
  defaultBadge: string;
  expiringSoon: string;
  expired: string;
  empty: string;
  unavailable: string;
  /** Why the only card on an active subscription cannot be detached. */
  lastCardLocked: string;
}

const DEFAULT_LABELS: SavedCardListLabels = {
  card: 'Card',
  expires: 'Expires',
  addCard: 'Add card',
  setDefault: 'Make default',
  remove: 'Remove',
  defaultBadge: 'Default',
  expiringSoon: 'Expires soon',
  expired: 'Expired',
  empty: 'No card on file.',
  unavailable: 'Card management is not available for this account.',
  lastCardLocked: 'Renewals need a card — add another one first.',
};

/** `visa` → `Visa`. Display only; never branch on a brand. */
function formatBrand(brand: string): string {
  if (!brand) return 'Card';
  return brand.charAt(0).toUpperCase() + brand.slice(1);
}

interface CardRow {
  card: SavedCard;
  label: string;
  expiry: string;
  expired: boolean;
  expiringSoon: boolean;
  /** Detaching the only card would leave renewals with nothing to charge. */
  removalLocked: boolean;
}

export function SavedCardList({
  phase,
  onAddCard,
  onSetDefault,
  onRemove,
  busy = false,
  labels,
  className,
}: SavedCardListProps) {
  const text = { ...DEFAULT_LABELS, ...labels };

  // Not memoized: a customer has a handful of cards, and this surface renders
  // on one page. Memoizing here would buy nothing and hide the derivation.
  const cards = cardsOf(phase);
  const now = new Date();
  const rows: CardRow[] = cards.map((card) => ({
    card,
    label: `${formatBrand(card.brand)} ···· ${card.last4}`,
    expiry: formatCardExpiry(card),
    expired: isCardExpired(card, now),
    expiringSoon: isCardExpiringSoon(card, now),
    removalLocked: cards.length === 1,
  }));

  if (phase.kind === 'unavailable') {
    return (
      <div className={className}>
        <p className="text-muted-foreground py-6 text-center text-sm">{text.unavailable}</p>
      </div>
    );
  }

  // A reserved-height skeleton, not nothing: this lane crosses the network, so
  // content appearing seconds later would read as a bug rather than as loading.
  if (phase.kind === 'loading') {
    return (
      <div className={`space-y-2 ${className ?? ''}`}>
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  const showActions = Boolean(onSetDefault || onRemove);
  const columnCount = showActions ? 4 : 3;

  return (
    <div className={`space-y-3 ${className ?? ''}`}>
      {phase.kind === 'error' ? (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{phase.message}</AlertDescription>
        </Alert>
      ) : null}

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{text.card}</TableHead>
            <TableHead>{text.expires}</TableHead>
            <TableHead />
            {showActions ? <TableHead className="text-right" /> : null}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length === 0 ? (
            <TableRow>
              <TableCell colSpan={columnCount} className="text-muted-foreground py-8 text-center">
                {text.empty}
              </TableCell>
            </TableRow>
          ) : (
            rows.map((row) => (
              <TableRow key={row.card.id}>
                <TableCell className="flex items-center gap-2 font-medium">
                  <CreditCard className="text-muted-foreground h-4 w-4" aria-hidden />
                  {row.label}
                </TableCell>
                <TableCell>{row.expiry}</TableCell>
                <TableCell className="space-x-1">
                  {row.card.isDefault ? (
                    <Badge variant="secondary">{text.defaultBadge}</Badge>
                  ) : null}
                  {row.expired ? (
                    <Badge variant="destructive">{text.expired}</Badge>
                  ) : row.expiringSoon ? (
                    <Badge variant="outline">{text.expiringSoon}</Badge>
                  ) : null}
                </TableCell>
                {showActions ? (
                  <TableCell className="space-x-2 text-right whitespace-nowrap">
                    {onSetDefault && !row.card.isDefault ? (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        disabled={busy}
                        onClick={() => onSetDefault(row.card.id)}
                      >
                        {text.setDefault}
                      </Button>
                    ) : null}
                    {onRemove ? (
                      // Disabled WITH a reason, never hidden: a control that
                      // vanishes reads as a bug, one that explains itself teaches.
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        disabled={busy || row.removalLocked}
                        title={row.removalLocked ? text.lastCardLocked : undefined}
                        onClick={() => onRemove(row.card.id)}
                      >
                        {text.remove}
                      </Button>
                    ) : null}
                  </TableCell>
                ) : null}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {onAddCard ? (
        <Button type="button" variant="outline" disabled={busy} onClick={onAddCard}>
          <Plus className="mr-1 h-4 w-4" aria-hidden />
          {text.addCard}
        </Button>
      ) : null}
    </div>
  );
}
