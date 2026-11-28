// ============================================================================
// @djangocfg/payments - Provider-agnostic React payments module (Stripe-first)
// ============================================================================
// The host injects ONE adapter (mock or stripe) via <PaymentProvider>.
// Package code depends only on the domain types + the adapter seam — never on
// a concrete SDK or a generated API client.
//
// @stripe/* is a RUNTIME dependency of two files (stripe-adapter.ts,
// StripePaymentElement.tsx) and a type-only one of a third (appearance.ts).
// It ships as a regular dep — stripe-js is just the CDN loader — and
// tree-shakes out of mock-only bundles. Enforced by
// scripts/check-stripe-imports.mjs, because this rule was stated in four
// comments and checked by none until it had already drifted.

// Domain (types + money helpers)
export * from './domain';

// Provider context (the injected transport seam)
export { PaymentProvider, usePaymentAdapter } from './context/PaymentProvider';
export type { PaymentProviderProps } from './context/PaymentProvider';

// Checkout guard (dialog-owned in-flight lock — gates accidental close)
export {
  CheckoutGuardProvider,
  useCheckoutGuard,
  usePublishCheckoutStatus,
  isCheckoutLocked,
} from './context/CheckoutGuard';

// Transport adapters (mock + stripe)
// `loadStripe` / `Stripe` are re-exported so hosts never declare @stripe/*
// themselves (the SDK is this package's dependency).
export {
  createMockPaymentAdapter,
  createStripeAdapter,
  loadStripe,
} from './transport';
export type {
  MockAdapterConfig,
  MockOutcome,
  StripeAdapterConfig,
  BackendIntent,
  BackendSubscription,
  BackendSetupIntent,
  BackendSavedCard,
  Stripe,
} from './transport';

// Hooks
export { useCheckout, usePaymentHistory, useSavedCards, useCardSetup } from './hooks';
export type {
  UseCheckoutResult,
  UsePaymentHistoryProps,
  UsePaymentHistoryResult,
  UseSavedCardsProps,
  UseSavedCardsResult,
  UseCardSetupResult,
} from './hooks';

// Components
export {
  CheckoutDialog,
  CheckoutForm,
  StripePaymentElement,
  DEFAULT_PAYMENT_ELEMENT_OPTIONS,
  buildStripeAppearance,
  PaymentHistory,
  PaymentStatusBadge,
  SavedCardList,
  CardSetupForm,
  UpdateCardDialog,
} from './components';
export type {
  CheckoutDialogProps,
  CheckoutFormProps,
  StripePaymentElementProps,
  StripeElementsContext,
  AppearanceTokens,
  PaymentHistoryProps,
  PaymentStatusBadgeProps,
  SavedCardListProps,
  SavedCardListLabels,
  CardSetupFormProps,
  UpdateCardDialogProps,
} from './components';
