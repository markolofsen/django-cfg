'use client';

// ============================================================================
// @djangocfg/payments — CheckoutForm (provider-agnostic form shell)
// ============================================================================
// ui-core only — no Stripe import. The provider's payment field (Stripe
// PaymentElement, or a mock input) is injected via the `paymentField` slot.
// Drives the checkout via useCheckout(); the host supplies labels (i18n).
//
// Stripe-like composition: order summary on top → divider → payment field →
// one prominent CTA → secure footer. Clean hierarchy, lots of air.

import React, { useCallback } from 'react';
import { Alert, AlertDescription, Button, Separator, Spinner } from '@djangocfg/ui-core';
import { Lock, ShieldCheck, AlertTriangle } from 'lucide-react';
import { useCheckout, type UseCheckoutResult } from '../hooks/useCheckout';
import { usePublishCheckoutStatus, isCheckoutLocked } from '../context/CheckoutGuard';
import { formatAmount } from '../domain/money';
import type { Currency, MinorUnits, PaymentReference } from '../domain/types';

export interface CheckoutFormProps {
  amount: MinorUnits;
  currency: Currency;
  reference: PaymentReference;
  /** Summary line-item title (e.g. the order description). Renders the top block. */
  summaryTitle?: string;
  /** Secondary summary line (e.g. "Billed monthly"). */
  summaryNote?: string;
  /** Slot for the provider's payment field (Stripe PaymentElement / mock input). */
  paymentField?: React.ReactNode;
  /**
   * Mock mode (no real Stripe key). Renders a friendly `4242…` placeholder when
   * no `paymentField` is supplied. On the real Stripe path this MUST be false so
   * an absent slot never falls through to the mock stub (that was the duplicate
   * card block under the real PaymentElement).
   */
  isMock?: boolean;
  /**
   * Confirm payload passed straight to the adapter (e.g. a Stripe Elements
   * instance). For the mock adapter this can be undefined.
   */
  elementsContext?: unknown;
  /** Where the provider returns after a redirect (3DS / hosted). */
  returnUrl?: string;
  onSuccess?: (intentId: string) => void;
  onFailure?: (error: string) => void;
  onCancel?: () => void;
  /** Default: `Pay {amount}`. */
  submitLabel?: string;
  cancelLabel?: string;
  /** Field label above the payment input. Default "Card". */
  fieldLabel?: string;
  /** Locale for amount formatting. */
  locale?: string;
  className?: string;
  /**
   * Share the PARENT's checkout state machine instead of creating a private one.
   * Pass this when the parent already created the intent/subscription (via
   * `start` / `startSubscription`) so the form confirms THAT intent rather than
   * spinning up a second `useCheckout` (which would create a duplicate
   * intent/subscription on submit). When omitted, the form is self-driving and
   * lazily creates a one-time intent on submit (legacy one-time path).
   */
  checkout?: UseCheckoutResult;
}

export function CheckoutForm({
  amount,
  currency,
  reference: _reference,
  summaryTitle,
  summaryNote,
  paymentField,
  isMock = false,
  elementsContext,
  returnUrl,
  onSuccess,
  onFailure,
  onCancel,
  submitLabel,
  cancelLabel = 'Cancel',
  fieldLabel = 'Card',
  locale,
  className,
  checkout,
}: CheckoutFormProps) {
  // Use the parent's shared machine when provided; else self-drive (one-time).
  // Hooks run unconditionally (Rules of Hooks); we just pick which result wins.
  const ownCheckout = useCheckout();
  const { status, error, isBusy, start, confirm, intent } = checkout ?? ownCheckout;
  const isShared = Boolean(checkout);

  // Publish status into the dialog's CheckoutGuard so the shell can block
  // Esc / overlay-click / × while a charge is in flight (no-op if there's no
  // guard, e.g. a standalone form).
  usePublishCheckoutStatus(status);
  const locked = isCheckoutLocked(status);

  const formatted = formatAmount(amount, currency, locale);
  const isDone = status === 'succeeded';
  const needsAction = status === 'requires_action';

  // A ref, because the disabled button is not a lock. `start` leaves status at
  // `requires_payment` before `confirm` sets `processing`, so between the two
  // awaits `isBusy` is false and the button is live again — and a second Enter
  // there would skip `start` (intent now set) and confirm the SAME intent
  // twice. A ref flips synchronously, with no render in between.
  const submittingRef = React.useRef(false);

  const handlePay = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (submittingRef.current) return;
      submittingRef.current = true;
      try {
        // Self-driving mode only: lazily create the one-time intent on first
        // submit. In shared mode the parent already created the intent/subscription
        // (start / startSubscription) — creating another here would duplicate it,
        // so we go straight to confirm.
        if (!isShared && !intent) {
          // `start` reports its own failure through status/error. Confirming
          // anyway would replace that reason with a generic "not ready to
          // confirm", hiding why the payment could not be created.
          const created = await start({ amount, currency, reference: _reference });
          if (!created) return;
        }
        await confirm(elementsContext, returnUrl);
      } finally {
        submittingRef.current = false;
      }
    },
    [isShared, intent, start, amount, currency, _reference, confirm, elementsContext, returnUrl],
  );

  // Fire host callbacks on terminal states.
  React.useEffect(() => {
    if (status === 'succeeded' && intent) onSuccess?.(intent.id);
    if (status === 'failed' && error) onFailure?.(error);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  return (
    <form onSubmit={handlePay} className={className}>
      <div className="space-y-5">
        {/* Summary block — what you're paying for + the amount. */}
        {summaryTitle ? (
          <div className="space-y-1">
            <p className="text-foreground text-sm font-medium leading-snug">{summaryTitle}</p>
            <p className="text-muted-foreground text-sm">
              <span className="text-foreground font-semibold">{formatted}</span>
              {summaryNote ? <span> · {summaryNote}</span> : null}
            </p>
          </div>
        ) : null}

        {summaryTitle ? <Separator /> : null}

        {/* Payment field. No mini "CARD" label — the accordion self-labels its
            rows, so the extra uppercase caption was redundant chrome (plan7). */}
        <div>
          {paymentField ? (
            <div className="min-h-[40px]">{paymentField}</div>
          ) : isMock ? (
            <div className="space-y-2">
              <p className="text-muted-foreground text-xs font-medium uppercase tracking-wide">
                {fieldLabel}
              </p>
              <div className="border-border bg-muted/30 text-muted-foreground flex h-10 items-center rounded-md border px-3 text-sm">
                4242 4242 4242 4242
              </div>
            </div>
          ) : null}
        </div>

        {error ? (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        {needsAction ? (
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Additional authentication is required to complete this payment.
            </AlertDescription>
          </Alert>
        ) : null}

        {/* Primary CTA. */}
        <Button type="submit" size="lg" className="w-full" disabled={isBusy || isDone}>
          {isBusy ? (
            <>
              <Spinner className="mr-1.5 h-4 w-4" />
              Processing…
            </>
          ) : isDone ? (
            <>
              <ShieldCheck className="mr-1.5 h-4 w-4" />
              Paid
            </>
          ) : (
            (submitLabel ?? `Pay ${formatted}`)
          )}
        </Button>

        {/* Hide the dismiss control entirely while a charge is in flight — no
            competing action, and closing now would orphan the intent. */}
        {onCancel && !locked ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="text-muted-foreground w-full"
            onClick={onCancel}
            disabled={isBusy}
          >
            {cancelLabel}
          </Button>
        ) : null}

        {/* Secure footer. */}
        <p className="text-muted-foreground flex items-center justify-center gap-1.5 text-xs">
          <Lock className="h-3 w-3" />
          Secure payment · Powered by Stripe
        </p>
      </div>
    </form>
  );
}
