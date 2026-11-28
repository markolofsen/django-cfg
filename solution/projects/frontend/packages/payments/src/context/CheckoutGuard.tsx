'use client';

// ============================================================================
// @djangocfg/payments — CheckoutGuard (the dialog's own checkout context)
// ============================================================================
// A tiny context shared by a checkout dialog and its inner form so BOTH read
// ONE source of truth for "is a payment in flight". The inner form (which owns
// the useCheckout machine) publishes its status up; the outer <Dialog> reads
// `canClose` to gate Esc / overlay-click / the × button, and any component in
// the tree can read the same status.
//
// Why a context and not props: the dialog shell and the form are on opposite
// sides of the Stripe <Elements> boundary — threading a setter through
// StripePaymentElement's render prop would be brittle. The provider wraps the
// whole dialog; the form pushes status via `usePublishCheckoutStatus`, the shell
// consumes via `useCheckoutGuard`. Matches @rules_2.0 03-DIALOGS (registry owns
// open/close; this owns the in-flight lock, orthogonally).

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { PaymentStatus } from '../domain/types';

/**
 * Statuses during which the dialog MUST NOT close — a charge is mid-flight or
 * awaiting 3DS, and tearing down <Elements> now would orphan the intent.
 */
export function isCheckoutLocked(status: PaymentStatus): boolean {
  return status === 'processing' || status === 'requires_action';
}

interface CheckoutGuardValue {
  readonly status: PaymentStatus;
  /** False while a payment is in flight / awaiting action. */
  readonly canClose: boolean;
  readonly setStatus: (status: PaymentStatus) => void;
}

const CheckoutGuardContext = createContext<CheckoutGuardValue | null>(null);

export function CheckoutGuardProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<PaymentStatus>('idle');
  const value = useMemo<CheckoutGuardValue>(
    () => ({ status, canClose: !isCheckoutLocked(status), setStatus }),
    [status],
  );
  return (
    <CheckoutGuardContext.Provider value={value}>
      {children}
    </CheckoutGuardContext.Provider>
  );
}

/**
 * Read the guard from the dialog shell. Returns `canClose` (false while locked)
 * plus the live status. Safe outside a provider — defaults to "can close".
 */
export function useCheckoutGuard(): Pick<CheckoutGuardValue, 'status' | 'canClose'> {
  const ctx = useContext(CheckoutGuardContext);
  if (!ctx) return { status: 'idle', canClose: true };
  return { status: ctx.status, canClose: ctx.canClose };
}

/**
 * Inner-form hook: pushes the live checkout status into the guard so the shell
 * can gate close. No-op when rendered outside a provider (e.g. a standalone
 * form). Also installs a `beforeunload` guard while locked so a full-page
 * refresh mid-confirm prompts the user.
 */
export function usePublishCheckoutStatus(status: PaymentStatus): void {
  const ctx = useContext(CheckoutGuardContext);
  const setStatus = ctx?.setStatus;

  useEffect(() => {
    setStatus?.(status);
  }, [setStatus, status]);

  const locked = isCheckoutLocked(status);
  useEffect(() => {
    if (!locked) return;
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      // Legacy Chrome requires a returnValue to trigger the prompt.
      e.returnValue = '';
    };
    window.addEventListener('beforeunload', onBeforeUnload);
    return () => window.removeEventListener('beforeunload', onBeforeUnload);
  }, [locked]);
}
