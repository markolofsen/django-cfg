'use client';

// ============================================================================
// @djangocfg/payments — UpdateCardDialog
// ============================================================================
// The whole add-a-card flow in one mountable surface: create the SetupIntent
// on open → render the provider's field against its clientSecret → confirm →
// report. ui-core + package internals only; the Stripe field arrives from the
// host through `renderPaymentField`, so this file imports no SDK.
//
// THE INTENT IS CREATED ON OPEN, NOT ON SUBMIT. CheckoutForm can create its
// intent lazily because it owns a mock-friendly text field. <Elements> cannot:
// it needs the clientSecret BEFORE it mounts, and remounting it after a submit
// would wipe whatever the customer typed. So opening the dialog starts the
// intent, and closing it resets the machine — an abandoned SetupIntent costs
// nothing and expires on its own.

import React, { useCallback, useEffect } from 'react';
import { Alert, AlertDescription, Button, Spinner } from '@djangocfg/ui-core';
import { AlertTriangle } from 'lucide-react';
import { CheckoutDialog } from './CheckoutDialog';
import { CardSetupForm } from './CardSetupForm';
import { useCardSetup } from '../hooks/useCardSetup';
import type { SaveCardInput } from '../domain/types';

export interface UpdateCardDialogProps {
  open: boolean;
  /** Called on any allowed close path. The machine resets itself. */
  onClose: () => void;
  /** Attach the saved card to this subscription's default. */
  subscriptionId?: string;
  /**
   * Render the whole card step against the live clientSecret. The host mounts
   * the provider's field (typically <StripePaymentElement>) and calls
   * `renderForm` from inside its render prop, handing back the live elements
   * context — which is what keeps this file free of @stripe/*.
   *
   * The two arrive TOGETHER on purpose: the elements context only exists
   * inside <Elements>, so a callback that reported it upward would have to
   * write state during the host's render. Passing the form INTO that scope
   * needs no state at all.
   */
  renderCardStep?: (args: {
    clientSecret: string;
    /** Render the form with the live provider context and its field node. */
    renderForm: (args: { elementsContext: unknown; field: React.ReactNode }) => React.ReactNode;
  }) => React.ReactNode;
  /** Mock path: renders the 4242 stub instead of a provider field. */
  isMock?: boolean;
  returnUrl?: string;
  /** Fired after Stripe stored the card. NOT proof the subscription recovered. */
  onSaved?: (setupIntentId: string) => void;
  title?: React.ReactNode;
  description?: React.ReactNode;
  submitLabel?: string;
  consentText?: string;
  className?: string;
}

export function UpdateCardDialog({
  open,
  onClose,
  subscriptionId,
  renderCardStep,
  isMock = false,
  returnUrl,
  onSaved,
  title = 'Add a card',
  description = 'Save a card for future renewals.',
  submitLabel,
  consentText,
  className,
}: UpdateCardDialogProps) {
  const setup = useCardSetup();
  const { start, reset, status, error, intent, supported } = setup;

  const input: SaveCardInput | undefined = subscriptionId ? { subscriptionId } : undefined;

  useEffect(() => {
    if (!open) {
      reset();
      return;
    }
    if (supported) void start(input);
    // `input` is derived from subscriptionId; re-running on open is the intent.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, supported, subscriptionId]);

  const handleSuccess = useCallback(
    (setupIntentId: string) => {
      onSaved?.(setupIntentId);
    },
    [onSaved],
  );

  let body: React.ReactNode;

  if (!supported) {
    body = (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          This account cannot save a card. Contact support to update your billing details.
        </AlertDescription>
      </Alert>
    );
  } else if (status === 'creating' || (!intent && status !== 'failed')) {
    body = (
      <div className="flex flex-col items-center gap-2 py-8">
        <Spinner className="h-5 w-5" />
        <p className="text-muted-foreground text-sm">Preparing the secure form…</p>
      </div>
    );
  } else if (!intent) {
    // Creation failed: the form would have no clientSecret to render against,
    // so offer the retry here rather than an empty card field.
    body = (
      <div className="space-y-3 py-2">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error ?? 'Could not open the card form.'}</AlertDescription>
        </Alert>
        <Button type="button" variant="outline" className="w-full" onClick={() => void start(input)}>
          Retry
        </Button>
      </div>
    );
  } else {
    const renderForm = ({
      elementsContext,
      field,
    }: {
      elementsContext: unknown;
      field: React.ReactNode;
    }) => (
      <CardSetupForm
        setup={setup}
        isMock={isMock}
        elementsContext={elementsContext}
        paymentField={field}
        returnUrl={returnUrl}
        submitLabel={submitLabel}
        consentText={consentText}
        onSuccess={handleSuccess}
        onCancel={onClose}
      />
    );

    body = renderCardStep
      ? renderCardStep({ clientSecret: intent.clientSecret, renderForm })
      : renderForm({ elementsContext: undefined, field: undefined });
  }

  return (
    <CheckoutDialog
      open={open}
      onClose={onClose}
      title={title}
      description={description}
      className={className}
    >
      {body}
    </CheckoutDialog>
  );
}
