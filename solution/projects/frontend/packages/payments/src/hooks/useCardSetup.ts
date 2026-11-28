'use client';

// ============================================================================
// @djangocfg/payments — useCardSetup (save a card, charge nothing now)
// ============================================================================
// The state machine for putting a card on file:
//   idle → creating → requires_payment → processing → succeeded | failed | requires_action
//
// Deliberately the SAME PaymentStatus vocabulary as useCheckout. One status
// union across the package means <PaymentStatusBadge> and every host branch
// read one set of names, not two that mean the same things.
//
// What it is NOT: proof that a subscription recovered. A succeeded SetupIntent
// means Stripe stored the card. Whether the open invoice then gets paid is a
// server decision reported by webhook — see the track's §6.

import { useCallback, useRef, useState } from 'react';
import { usePaymentAdapter } from '../context/PaymentProvider';
import type {
  ConfirmArgs,
  PaymentStatus,
  SaveCardInput,
  SetupIntent,
} from '../domain/types';

export interface UseCardSetupResult {
  status: PaymentStatus;
  /** The SetupIntent once created; its clientSecret drives <StripePaymentElement>. */
  intent: SetupIntent | null;
  error: string | null;
  /** Set when the provider needs a redirect / 3DS step. */
  nextActionUrl: string | null;
  /** Whether the adapter can save a card at all. */
  supported: boolean;
  /** Step 1: create the SetupIntent. Resolves with it, or undefined on failure. */
  start: (input?: SaveCardInput) => Promise<SetupIntent | undefined>;
  /** Step 2: confirm with the provider (Stripe Elements or mock). */
  confirm: (
    elementsContext?: ConfirmArgs['elementsContext'],
    returnUrl?: string,
  ) => Promise<void>;
  reset: () => void;
  /** True while a network step is in flight. */
  isBusy: boolean;
}

export function useCardSetup(): UseCardSetupResult {
  const adapter = usePaymentAdapter();
  const supported = typeof adapter.createSetupIntent === 'function';

  const [status, setStatus] = useState<PaymentStatus>('idle');
  const [intent, setIntent] = useState<SetupIntent | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [nextActionUrl, setNextActionUrl] = useState<string | null>(null);

  // Latest intent for confirm() without a stale closure — same device as
  // useCheckout's intentRef.
  const intentRef = useRef<SetupIntent | null>(null);

  const reset = useCallback(() => {
    setStatus('idle');
    setIntent(null);
    setError(null);
    setNextActionUrl(null);
    intentRef.current = null;
  }, []);

  const start = useCallback(
    async (input?: SaveCardInput) => {
      setError(null);
      setNextActionUrl(null);
      setStatus('creating');
      if (!adapter.createSetupIntent) {
        setStatus('failed');
        setError('This payment provider cannot save a card.');
        return undefined;
      }
      try {
        const created = await adapter.createSetupIntent(input);
        intentRef.current = created;
        setIntent(created);
        setStatus('requires_payment');
        return created;
      } catch (e) {
        setStatus('failed');
        setError(e instanceof Error ? e.message : 'Failed to start saving the card.');
        return undefined;
      }
    },
    [adapter],
  );

  const confirm = useCallback(
    async (elementsContext?: ConfirmArgs['elementsContext'], returnUrl?: string) => {
      const current = intentRef.current;
      if (!current?.clientSecret) {
        setStatus('failed');
        setError('The card form is not ready to submit.');
        return;
      }

      setError(null);
      setStatus('processing');
      try {
        // `confirmType: 'setup'` is what dispatches stripe.confirmSetup. The
        // adapter already sends mandate_data.customer_acceptance with it, which
        // is what makes the stored card chargeable off-session at renewal.
        const result = await adapter.confirm({
          clientSecret: current.clientSecret,
          elementsContext,
          returnUrl,
          confirmType: 'setup',
        });
        setStatus(result.status);
        if (result.error) setError(result.error);
        if (result.nextActionUrl) setNextActionUrl(result.nextActionUrl);
      } catch (e) {
        setStatus('failed');
        setError(e instanceof Error ? e.message : 'Could not save your card.');
      }
    },
    [adapter],
  );

  const isBusy = status === 'creating' || status === 'processing';

  return {
    status,
    intent,
    error,
    nextActionUrl,
    supported,
    start,
    confirm,
    reset,
    isBusy,
  };
}
