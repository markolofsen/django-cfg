// ============================================================================
// @djangocfg/payments — transport barrel
// ============================================================================

export { createMockPaymentAdapter } from './mock-adapter';
export type { MockAdapterConfig, MockOutcome } from './mock-adapter';

export { createStripeAdapter, loadStripe } from './stripe-adapter';
export type {
  StripeAdapterConfig,
  BackendIntent,
  BackendSubscription,
  BackendSetupIntent,
  BackendSavedCard,
  Stripe,
} from './stripe-adapter';
