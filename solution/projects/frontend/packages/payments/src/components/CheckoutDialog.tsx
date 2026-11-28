'use client';

// ============================================================================
// @djangocfg/payments — CheckoutDialog
// ============================================================================
// The host-agnostic dialog shell around a checkout body. Every consumer used
// to re-write this glue (see cmdop's PaymentCheckoutShell): a Dialog whose
// close paths (Esc / overlay-click / ×) are gated while a charge is in flight,
// wired to the CheckoutGuard context that the inner CheckoutForm publishes
// into via usePublishCheckoutStatus.
//
// Layout invariant: the body is height-capped and scrolls INSIDE the dialog
// (header stays pinned), so the Stripe Payment Element never clips on small
// viewports.
//
// The children are the host's checkout body — typically the intent-creation
// state machine ending in <CheckoutForm> (with <StripePaymentElement> on the
// real path). This shell owns open/close + the in-flight lock, nothing else.

import { type ReactNode } from 'react';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@djangocfg/ui-core';

import { CheckoutGuardProvider, useCheckoutGuard } from '../context/CheckoutGuard';

export interface CheckoutDialogProps {
  open: boolean;
  /** Called on any allowed close path (Esc / overlay / ×). */
  onClose: () => void;
  /** Dialog heading. Host supplies translated text. */
  title?: ReactNode;
  /**
   * Accessible description (rendered sr-only). Screen readers announce it;
   * sighted users see the checkout body itself.
   */
  description?: ReactNode;
  /** Extra classes for the DialogContent (e.g. a wider max-w). */
  className?: string;
  children: ReactNode;
}

/**
 * Checkout dialog shell: `CheckoutGuardProvider` + close-locked `Dialog`.
 * While the inner form reports `processing` / `requires_action`, every close
 * path is disabled and the × button is hidden — tearing down the form
 * mid-confirm would orphan the payment intent.
 */
export function CheckoutDialog({
  open,
  onClose,
  title = 'Checkout',
  description = 'Complete your payment.',
  className,
  children,
}: CheckoutDialogProps) {
  return (
    <CheckoutGuardProvider>
      <CheckoutDialogShell
        open={open}
        onClose={onClose}
        title={title}
        description={description}
        className={className}
      >
        {children}
      </CheckoutDialogShell>
    </CheckoutGuardProvider>
  );
}

/** Inner shell — must live under the provider to read the guard. */
function CheckoutDialogShell({
  open,
  onClose,
  title,
  description,
  className,
  children,
}: CheckoutDialogProps) {
  const { canClose } = useCheckoutGuard();

  const handleOpenChange = (next: boolean) => {
    if (!next && canClose) onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        className={[
          'flex max-h-[88vh] flex-col gap-0 sm:max-w-md',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
        closeButton={canClose ? undefined : false}
        onEscapeKeyDown={(e) => {
          if (!canClose) e.preventDefault();
        }}
        onInteractOutside={(e) => {
          if (!canClose) e.preventDefault();
        }}
      >
        <DialogHeader className="pb-4">
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription className="sr-only">{description}</DialogDescription>
        </DialogHeader>

        {/* Scroll container: negative margin + padding keeps the scrollbar
            out of the content gutter. */}
        <div className="-mr-2 min-h-0 flex-1 overflow-y-auto overscroll-contain pr-2">
          {children}
        </div>
      </DialogContent>
    </Dialog>
  );
}
