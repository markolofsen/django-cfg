'use client';

// ============================================================================
// @djangocfg/payments — CardSetupForm (save a card, charge nothing)
// ============================================================================
// ui-core only — no Stripe import; the provider's field arrives via the
// `paymentField` slot, exactly as CheckoutForm takes it.
//
// NOT CheckoutForm with amount=0. That form is built around a sum: its CTA
// reads `Pay {amount}`, its summary states what is being bought, its success
// state says "Paid". A card being saved has no amount, buys nothing, and ends
// at "Card saved" — passing a meaningless zero through all three would produce
// a form that lies in three places.
//
// CONSENT IS NOT DECORATION. Stripe's `mandate_data.customer_acceptance` is
// sent as `infer_from_client`, which derives the mandate from the text ON
// SCREEN. `consentText` is that text. Off-session charging requires it, so the
// component renders a default rather than allowing an empty one.

import React, { useCallback, useRef } from 'react';
import { Alert, AlertDescription, Button, Spinner } from '@djangocfg/ui-core';
import { AlertTriangle, Lock, ShieldCheck } from 'lucide-react';
import { isCheckoutLocked, usePublishCheckoutStatus } from '../context/CheckoutGuard';
import type { UseCardSetupResult } from '../hooks/useCardSetup';

export interface CardSetupFormProps {
  /** The setup machine, created by the parent so it also owns the clientSecret. */
  setup: UseCardSetupResult;
  /** Slot for the provider's card field (Stripe PaymentElement / mock input). */
  paymentField?: React.ReactNode;
  /** Renders a `4242…` stub when no `paymentField` is supplied. Mock path only. */
  isMock?: boolean;
  /** Confirm payload passed to the adapter (a Stripe Elements instance). */
  elementsContext?: unknown;
  /** Where the provider returns after a 3DS redirect. */
  returnUrl?: string;
  onSuccess?: (setupIntentId: string) => void;
  onFailure?: (error: string) => void;
  onCancel?: () => void;
  submitLabel?: string;
  cancelLabel?: string;
  /** The mandate text. Shown to the customer AND inferred by Stripe. */
  consentText?: string;
  className?: string;
}

const DEFAULT_CONSENT =
  'By saving this card you authorise us to charge it for your subscription renewals, including when you are not present.';

export function CardSetupForm({
  setup,
  paymentField,
  isMock = false,
  elementsContext,
  returnUrl,
  onSuccess,
  onFailure,
  onCancel,
  submitLabel = 'Save card',
  cancelLabel = 'Cancel',
  consentText = DEFAULT_CONSENT,
  className,
}: CardSetupFormProps) {
  const { status, error, isBusy, confirm, intent } = setup;

  // Same guard CheckoutForm publishes into: a SetupIntent mid-confirm is a
  // real authorisation with the issuer, so the dialog must not close over it.
  usePublishCheckoutStatus(status);
  const locked = isCheckoutLocked(status);

  const isDone = status === 'succeeded';
  const needsAction = status === 'requires_action';

  // A ref, not the disabled prop: between `start` and `confirm` the status sits
  // at `requires_payment` with `isBusy` false, so a second Enter would confirm
  // the same SetupIntent twice. A ref flips with no render in between.
  const submittingRef = useRef(false);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (submittingRef.current) return;
      submittingRef.current = true;
      try {
        await confirm(elementsContext, returnUrl);
      } finally {
        submittingRef.current = false;
      }
    },
    [confirm, elementsContext, returnUrl],
  );

  React.useEffect(() => {
    if (status === 'succeeded' && intent) onSuccess?.(intent.id);
    if (status === 'failed' && error) onFailure?.(error);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  return (
    <form onSubmit={handleSubmit} className={className}>
      <div className="space-y-5">
        <div>
          {paymentField ? (
            <div className="min-h-[40px]">{paymentField}</div>
          ) : isMock ? (
            <div className="border-border bg-muted/30 text-muted-foreground flex h-10 items-center rounded-md border px-3 text-sm">
              4242 4242 4242 4242
            </div>
          ) : null}
        </div>

        <p className="text-muted-foreground text-xs leading-relaxed">{consentText}</p>

        {error ? (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        {needsAction ? (
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Your bank needs to confirm this card before it can be saved.
            </AlertDescription>
          </Alert>
        ) : null}

        <Button type="submit" size="lg" className="w-full" disabled={isBusy || isDone}>
          {isBusy ? (
            <>
              <Spinner className="mr-1.5 h-4 w-4" />
              Saving…
            </>
          ) : isDone ? (
            <>
              <ShieldCheck className="mr-1.5 h-4 w-4" />
              Card saved
            </>
          ) : (
            submitLabel
          )}
        </Button>

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

        <p className="text-muted-foreground flex items-center justify-center gap-1.5 text-xs">
          <Lock className="h-3 w-3" />
          Secure · Powered by Stripe
        </p>
      </div>
    </form>
  );
}
