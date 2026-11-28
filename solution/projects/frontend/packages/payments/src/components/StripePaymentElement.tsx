'use client';

// ============================================================================
// @djangocfg/payments — StripePaymentElement
// ============================================================================
// One of two files allowed a RUNTIME @stripe/* import (the other is
// stripe-adapter.ts). Enforced by scripts/check-stripe-imports.mjs.
// Wraps the Stripe <Elements> provider + <PaymentElement>, and exposes the
// live Elements instance to the host via a render prop so it can be handed to
// the adapter's confirm() (CheckoutForm's `elementsContext`).
//
// Theming: Stripe renders in a cross-origin iframe that app CSS can't touch, so
// we pass an `appearance` derived from the live ui-core design tokens (via
// useThemePalette) with `theme: 'night' | 'stripe'`. Without this the form is a
// WHITE box on our dark dialog. Appearance is MUTABLE — we update it in place on
// a theme toggle (see the <Elements> note below), we do NOT remount, so a
// half-typed card isn't wiped.
//
// Placement: the host decides where the card field goes. Instead of rendering
// <PaymentElement/> next to the children, we pass a ready-to-place node INTO
// the render prop, so the host can drop it under CheckoutForm's "CARD" label as
// the single `paymentField` (no duplicate mock stub).
//
// Load handling: loadStripe() REJECTS (does not resolve null) when Stripe.js
// can't load from the CDN (network/blocked). We await it explicitly so we can
// render an honest error + Retry instead of a stuck spinner or a misleading
// fallback. Only mount <Elements> once Stripe actually resolved.

import React, { useEffect, useMemo, useState } from 'react';
import { Elements, PaymentElement, useElements } from '@stripe/react-stripe-js';
import type {
  Stripe,
  StripeElementsOptionsClientSecret,
  StripePaymentElementOptions,
} from '@stripe/stripe-js';
import {
  Alert,
  AlertDescription,
  Button,
  Spinner,
  useResolvedTheme,
} from '@djangocfg/ui-core';
import { useThemePalette } from '@djangocfg/ui-core/styles/palette';
import { AlertTriangle } from 'lucide-react';
import { buildStripeAppearance } from './appearance';

/** Live elements context handed to the host for confirm(). */
export type StripeElementsContext = ReturnType<typeof useElements>;

/**
 * Card-focused defaults — the calm, single-column checkout (plan7).
 *
 * ACCORDION, not tabs. The old 4-tile tab grid (Card · Klarna · Cash App ·
 * Amazon Pay) was the main source of clutter — four equal-weight tiles for a
 * choice that is almost always "card". Accordion (Stripe's default since
 * 2025-03-31) shows the card form open and fillable, with any surviving
 * alternative methods as quiet collapsed rows below it:
 *   - `defaultCollapsed: false` → card form open immediately (no extra click).
 *   - `radios: 'never'` + `spacedAccordionItems: false` → the two cheapest
 *     height wins; tight rows, no radio column, no inter-item gaps.
 *
 * Which methods appear is driven by the intent (server-side / Dashboard), NOT
 * hand-pinned here: for a subscription Stripe auto-hides non-recurring methods,
 * so we don't need `paymentMethodOrder` to filter — dropping it also keeps
 * Link's inline prompt visible. Klarna is disabled in the Dashboard (heaviest
 * row, least subscription value); Cash App / Amazon Pay survive collapsed.
 *
 * Link is LEFT ON: it renders inline *inside* the card form (not a tall express
 * block), so it lifts conversion without bloating the dialog. Pass `email`
 * (and `phone` where available) below so returning Link users go straight to a
 * short OTP. We still suppress the tall Apple/Google Pay express blocks.
 * Prereq: Link enabled in Dashboard + domain registered — until then Link
 * simply doesn't render, so this is safe to ship ahead of it.
 */
export const DEFAULT_PAYMENT_ELEMENT_OPTIONS: StripePaymentElementOptions = {
  layout: {
    type: 'accordion',
    defaultCollapsed: false,
    radios: 'never',
    spacedAccordionItems: false,
  },
  wallets: { applePay: 'never', googlePay: 'never' },
  fields: { billingDetails: { address: 'never' } },
};

export interface StripePaymentElementProps {
  /** loadStripe(publishableKey), memoized once at host module scope. */
  stripe: Promise<Stripe | null>;
  /** Client secret created on the backend for this PaymentIntent. */
  clientSecret: string;
  /**
   * Render prop receiving the live Stripe Elements context AND a ready-to-place
   * <PaymentElement/> node. Pass `field` where you want the card input to
   * appear (e.g. CheckoutForm's `paymentField`) and `elements` to
   * <CheckoutForm elementsContext={elements}>.
   */
  children: (args: {
    elements: StripeElementsContext;
    field: React.ReactNode;
  }) => React.ReactNode;
  /** Optional Elements appearance/options overrides (merged after appearance). */
  options?: Omit<StripeElementsOptionsClientSecret, 'clientSecret' | 'appearance'>;
  /** Override the compact PaymentElement options (layout, wallets, fields…). */
  paymentElementOptions?: StripePaymentElementOptions;
  /**
   * Logged-in user's email. Passed to the PaymentElement as
   * `defaultValues.billingDetails.email` so Stripe Link can autofill / one-click
   * for returning users. Stripe recommends supplying it when available.
   */
  email?: string;
  /**
   * Logged-in user's phone (E.164). Prefilling it alongside email pre-targets
   * Link's SMS OTP so a returning user lands on the code with fewer fields —
   * shrinks Link's inline block. Optional; omit if unknown.
   */
  phone?: string;
  /**
   * Called when Stripe.js fails to load. The host can disable its own Pay
   * affordance, log, etc. Receives the error message.
   */
  onLoadError?: (message: string) => void;
}

type LoadState =
  | { phase: 'loading' }
  | { phase: 'ready'; stripe: Stripe }
  | { phase: 'error'; message: string };

/** Inner component: must live under <Elements> to call useElements(). */
function ElementsBridge({
  children,
  paymentElementOptions,
  email,
  phone,
}: {
  children: StripePaymentElementProps['children'];
  paymentElementOptions: StripePaymentElementOptions;
  email?: string;
  phone?: string;
}) {
  const elements = useElements();
  // Prefill email + phone so Stripe Link recognizes the returning user and
  // targets the SMS OTP immediately (shorter Link block). Merge (don't clobber)
  // any caller-provided defaultValues.
  const options = useMemo<StripePaymentElementOptions>(() => {
    if (!email && !phone) return paymentElementOptions;
    return {
      ...paymentElementOptions,
      defaultValues: {
        ...paymentElementOptions.defaultValues,
        billingDetails: {
          ...paymentElementOptions.defaultValues?.billingDetails,
          ...(email ? { email } : {}),
          ...(phone ? { phone } : {}),
        },
      },
    };
  }, [paymentElementOptions, email, phone]);
  const field = <PaymentElement options={options} />;
  return <>{children({ elements, field })}</>;
}

export function StripePaymentElement({
  stripe,
  clientSecret,
  children,
  options,
  paymentElementOptions = DEFAULT_PAYMENT_ELEMENT_OPTIONS,
  email,
  phone,
  onLoadError,
}: StripePaymentElementProps) {
  const [state, setState] = useState<LoadState>({ phase: 'loading' });
  // Bump to retry loading.
  const [attempt, setAttempt] = useState(0);

  // Drive the Stripe appearance from the live design tokens. useThemePalette
  // returns hex (safe for Stripe's core color vars); useResolvedTheme picks the
  // base 'night'/'stripe' theme and is the remount key.
  const theme = useResolvedTheme();
  const palette = useThemePalette();
  const appearance = useMemo(
    () =>
      buildStripeAppearance(theme, {
        primary: palette.primary,
        input: palette.input,
        foreground: palette.foreground,
        mutedForeground: palette.mutedForeground,
        border: palette.border,
        ring: palette.ring,
        destructive: palette.destructive,
      }),
    [theme, palette],
  );

  useEffect(() => {
    let active = true;
    setState({ phase: 'loading' });
    stripe
      .then((s) => {
        if (!active) return;
        if (s) {
          setState({ phase: 'ready', stripe: s });
        } else {
          const msg = 'Stripe is not configured.';
          setState({ phase: 'error', message: msg });
          onLoadError?.(msg);
        }
      })
      .catch((e: unknown) => {
        if (!active) return;
        const msg =
          e instanceof Error ? e.message : 'Failed to load the payment form.';
        setState({ phase: 'error', message: msg });
        onLoadError?.(msg);
      });
    return () => {
      active = false;
    };
    // `attempt` re-runs the load; `stripe` is a stable host-memoized promise.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stripe, attempt]);

  if (state.phase === 'loading') {
    return (
      <div className="flex flex-col items-center gap-2 py-8">
        <Spinner className="h-5 w-5" />
        <p className="text-muted-foreground text-sm">Loading secure payment form…</p>
      </div>
    );
  }

  if (state.phase === 'error') {
    return (
      <div className="space-y-3 py-2">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {state.message} Check your connection and try again.
          </AlertDescription>
        </Alert>
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => setAttempt((n) => n + 1)}
        >
          Retry
        </Button>
      </div>
    );
  }

  const elementsOptions: StripeElementsOptionsClientSecret = {
    ...options,
    clientSecret,
    appearance,
  };
  return (
    // NO `key={theme}` remount: @stripe/react-stripe-js diffs the `options` prop
    // and calls `elements.update({ appearance })` live for mutable keys
    // (appearance is mutable; only clientSecret/fonts are immutable). Remounting
    // on a theme flip would tear down the iframe and WIPE any half-typed card
    // details — updating in place re-themes without losing input.
    <Elements stripe={state.stripe} options={elementsOptions}>
      <ElementsBridge
        paymentElementOptions={paymentElementOptions}
        email={email}
        phone={phone}
      >
        {children}
      </ElementsBridge>
    </Elements>
  );
}
