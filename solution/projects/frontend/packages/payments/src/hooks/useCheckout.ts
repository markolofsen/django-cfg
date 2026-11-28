'use client';

// ============================================================================
// @djangocfg/payments — useCheckout (the checkout state machine)
// ============================================================================
// Owns the explicit state machine over the injected adapter:
//   idle → creating → requires_payment → processing → succeeded | failed | requires_action
// Reads the adapter via usePaymentAdapter(); never touches a concrete SDK.

import { useCallback, useRef, useState } from 'react';
import { usePaymentAdapter } from '../context/PaymentProvider';
import type {
  ConfirmArgs,
  ConfirmType,
  CreatePaymentInput,
  PaymentIntent,
  PaymentStatus,
  StartSubscriptionInput,
} from '../domain/types';

export interface UseCheckoutResult {
  status: PaymentStatus;
  intent: PaymentIntent | null;
  error: string | null;
  /** Set when the provider needs a redirect / 3DS step. */
  nextActionUrl: string | null;
  /** Step 1 (one-time): create the PaymentIntent → client_secret ready. */
  /** Resolves with the created intent, or undefined when creation failed. */
  start: (input: CreatePaymentInput) => Promise<PaymentIntent | undefined>;
  /**
   * Step 1 (subscription, deferred flow): create an `incomplete` Stripe
   * subscription on the backend → client_secret + confirmType ready. `confirm`
   * then dispatches confirmPayment vs confirmSetup automatically.
   */
  startSubscription: (input: StartSubscriptionInput) => Promise<void>;
  /** Step 2: confirm with the provider (Stripe Elements or mock). */
  confirm: (
    elementsContext?: ConfirmArgs['elementsContext'],
    returnUrl?: string,
  ) => Promise<void>;
  reset: () => void;
  /** True while a network step is in flight. */
  isBusy: boolean;
}

export function useCheckout(): UseCheckoutResult {
  const adapter = usePaymentAdapter();

  const [status, setStatus] = useState<PaymentStatus>('idle');
  const [intent, setIntent] = useState<PaymentIntent | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [nextActionUrl, setNextActionUrl] = useState<string | null>(null);

  // Keep the latest intent for confirm() without stale closures.
  const intentRef = useRef<PaymentIntent | null>(null);
  // Which confirm call step 2 must run (subscription setup vs payment). One-time
  // checkout leaves this at 'payment'.
  const confirmTypeRef = useRef<ConfirmType>('payment');

  const reset = useCallback(() => {
    setStatus('idle');
    setIntent(null);
    setError(null);
    setNextActionUrl(null);
    intentRef.current = null;
    confirmTypeRef.current = 'payment';
  }, []);

  const start = useCallback(
    async (input: CreatePaymentInput) => {
      setError(null);
      setNextActionUrl(null);
      setStatus('creating');
      confirmTypeRef.current = 'payment';
      try {
        const created = await adapter.createIntent(input);
        intentRef.current = created;
        setIntent(created);
        setStatus(created.status === 'idle' ? 'requires_payment' : created.status);
        // Returned so a caller can tell success from failure without reading
        // state that has not re-rendered yet.
        return created;
      } catch (e) {
        setStatus('failed');
        setError(e instanceof Error ? e.message : 'Failed to start payment.');
        return undefined;
      }
    },
    [adapter],
  );

  const startSubscription = useCallback(
    async (input: StartSubscriptionInput) => {
      setError(null);
      setNextActionUrl(null);
      setStatus('creating');
      if (!adapter.createSubscription) {
        setStatus('failed');
        setError('This payment provider does not support subscriptions.');
        return;
      }
      try {
        const sub = await adapter.createSubscription(input);
        confirmTypeRef.current = sub.confirmType;
        // Normalize into the same PaymentIntent shape the confirm step reads —
        // the subscription id stands in for `id`, the deferred client_secret
        // drives Elements exactly like a one-time intent.
        const asIntent: PaymentIntent = {
          id: sub.stripeSubscriptionId,
          clientSecret: sub.clientSecret,
          amount: 0,
          currency: 'usd',
          status: 'requires_payment',
          reference: { kind: 'subscription', id: sub.stripeSubscriptionId },
          provider: sub.provider,
          createdAt: new Date().toISOString(),
        };
        intentRef.current = asIntent;
        setIntent(asIntent);
        setStatus('requires_payment');
      } catch (e) {
        setStatus('failed');
        setError(e instanceof Error ? e.message : 'Failed to start subscription.');
      }
    },
    [adapter],
  );

  const confirm = useCallback(
    async (elementsContext?: ConfirmArgs['elementsContext'], returnUrl?: string) => {
      const current = intentRef.current;
      if (!current?.clientSecret) {
        setStatus('failed');
        setError('Payment is not ready to confirm.');
        return;
      }

      setError(null);
      setStatus('processing');
      try {
        const result = await adapter.confirm({
          clientSecret: current.clientSecret,
          elementsContext,
          returnUrl,
          confirmType: confirmTypeRef.current,
        });
        setStatus(result.status);
        if (result.error) setError(result.error);
        if (result.nextActionUrl) setNextActionUrl(result.nextActionUrl);

        const updated: PaymentIntent = { ...current, status: result.status };
        intentRef.current = updated;
        setIntent(updated);
      } catch (e) {
        setStatus('failed');
        setError(e instanceof Error ? e.message : 'Payment failed.');
      }
    },
    [adapter],
  );

  const isBusy = status === 'creating' || status === 'processing';

  return { status, intent, error, nextActionUrl, start, startSubscription, confirm, reset, isBusy };
}
