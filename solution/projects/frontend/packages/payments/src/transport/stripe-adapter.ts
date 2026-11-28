// ============================================================================
// @djangocfg/payments — Stripe adapter (transport layer, Stripe-specific)
// ============================================================================
// One of two files allowed a RUNTIME @stripe/* import (the other is
// StripePaymentElement.tsx; appearance.ts may name its types). Keeping the SDK
// isolated here keeps the mock-only path Stripe-free in the bundle and the
// domain/ layer SDK-free. Enforced by scripts/check-stripe-imports.mjs.
//
// The publishable key and the create-intent HTTP call are HOST
// responsibilities, passed in via StripeAdapterConfig — the package never
// reads env vars or imports the generated API client.

import type { Stripe, StripeElements } from '@stripe/stripe-js';

// Re-exported so hosts can build their memoized `getStripe()` without
// declaring @stripe/stripe-js themselves — the SDK stays this package's
// dependency and the "only 2 files import @stripe/*" rule holds.
export { loadStripe } from '@stripe/stripe-js';
export type { Stripe } from '@stripe/stripe-js';
import type {
  ConfirmArgs,
  ConfirmResult,
  CreatePaymentInput,
  PaymentIntent,
  PaymentPage,
  PaymentProviderAdapter,
  PaymentStatus,
  SavedCard,
  SaveCardInput,
  SetupIntent,
  StartSubscriptionInput,
  SubscriptionIntent,
} from '../domain/types';

/** Raw shape the host's backend returns from its create-intent endpoint. */
export interface BackendIntent {
  id: string;
  client_secret: string;
  status: string;
}

/**
 * Raw shape the host's backend returns from `subscribe-checkout` (paid branch).
 * Mirrors the Django `SubscribeCheckoutResult` (snake_case).
 */
export interface BackendSubscription {
  stripe_subscription_id: string;
  status: string;
  confirm_type: 'payment' | 'setup';
  client_secret: string | null;
}

/** Raw shape the host's backend returns from its create-setup-intent endpoint. */
export interface BackendSetupIntent {
  id: string;
  client_secret: string;
}

/** Raw saved-card row from the host's backend (snake_case, as Django serializes). */
export interface BackendSavedCard {
  id: string;
  brand: string;
  last4: string;
  exp_month: number;
  exp_year: number;
  is_default: boolean;
}

export interface StripeAdapterConfig {
  /** Resolved by the host: memoized loadStripe(publishableKey). */
  getStripe: () => Promise<Stripe | null>;
  /** Host transport call → POST /payments/intents → { id, client_secret, status }. */
  createIntentOnBackend: (input: CreatePaymentInput) => Promise<BackendIntent>;
  /**
   * Host transport call → POST /billing/subscribe-checkout/ (paid branch only) →
   * the raw `SubscribeCheckoutResult`. Injected by the host so the package never
   * touches the generated client. Omit on adapters that don't do subscriptions.
   */
  createSubscriptionOnBackend?: (input: StartSubscriptionInput) => Promise<BackendSubscription>;
  /** Optional history fetch (host transport → GET /payments). */
  listPaymentsOnBackend?: PaymentProviderAdapter['listPayments'];
  /**
   * Card on file. Wire all four or none — a host that lists cards but cannot
   * add one shows a dead end.
   *
   * SERVER-SIDE RULES this adapter cannot enforce:
   *  - create the SetupIntent against the STORED customer, never an id from
   *    the client;
   *  - `usage: 'off_session'` — renewals are off-session, and the default
   *    (`on_session`) stores a card Stripe declines at renewal time;
   *  - setting a default writes `invoice_settings.default_payment_method` on
   *    the customer AND `default_payment_method` on the subscription. Only the
   *    second governs an existing subscription; writing one is a quiet no-op.
   */
  createSetupIntentOnBackend?: (input?: SaveCardInput) => Promise<BackendSetupIntent>;
  listPaymentMethodsOnBackend?: () => Promise<BackendSavedCard[]>;
  setDefaultPaymentMethodOnBackend?: (id: string) => Promise<void>;
  removePaymentMethodOnBackend?: (id: string) => Promise<void>;
  /** Deterministic timestamp factory (tests). Defaults to `new Date()`. */
  now?: () => Date;
}

function mapSavedCard(raw: BackendSavedCard): SavedCard {
  return {
    id: raw.id,
    brand: raw.brand,
    last4: raw.last4,
    expMonth: raw.exp_month,
    expYear: raw.exp_year,
    isDefault: raw.is_default,
  };
}

/** Map a Stripe PaymentIntent status string to our normalized status. */
function mapStripeStatus(status: string): PaymentStatus {
  switch (status) {
    case 'requires_payment_method':
    case 'requires_confirmation':
      return 'requires_payment';
    case 'requires_action':
    case 'requires_capture':
      return 'requires_action';
    case 'processing':
      return 'processing';
    case 'succeeded':
      return 'succeeded';
    case 'canceled':
      return 'canceled';
    default:
      return 'failed';
  }
}

export function createStripeAdapter(
  cfg: StripeAdapterConfig,
): PaymentProviderAdapter {
  const now = cfg.now ?? (() => new Date());

  return {
    id: 'stripe',

    async createIntent(input: CreatePaymentInput): Promise<PaymentIntent> {
      const raw = await cfg.createIntentOnBackend(input);
      return {
        id: raw.id,
        clientSecret: raw.client_secret,
        amount: input.amount,
        currency: input.currency,
        status: mapStripeStatus(raw.status),
        reference: input.reference,
        provider: 'stripe',
        createdAt: now().toISOString(),
      };
    },

    async confirm(args: ConfirmArgs): Promise<ConfirmResult> {
      const stripe = await cfg.getStripe();
      if (!stripe) {
        return {
          status: 'failed',
          intentId: '',
          error: 'Stripe failed to initialize.',
        };
      }

      const elements = args.elementsContext as StripeElements | undefined;
      if (!elements) {
        return {
          status: 'failed',
          intentId: '',
          error: 'Missing Stripe Elements context.',
        };
      }

      // `mandate_data` is REQUIRED for recurring alt-methods (Cash App Pay,
      // Amazon Pay, SEPA…) or they silently fail to confirm on a subscription.
      // Harmless for card. `infer_from_client` lets Stripe derive the mandate
      // text from the on-screen agreement (research §2).
      const confirmParams = {
        ...(args.returnUrl ? { return_url: args.returnUrl } : {}),
        mandate_data: {
          customer_acceptance: {
            type: 'online' as const,
            online: { infer_from_client: true },
          },
        },
      };

      // Deferred subscription with nothing to charge now ($0 / trial): confirm a
      // SetupIntent to save the card for future renewals. Otherwise confirm the
      // (first-invoice) PaymentIntent. Same <Elements clientSecret> either way —
      // only the confirm call differs (research §1 branch).
      if (args.confirmType === 'setup') {
        const { error, setupIntent } = await stripe.confirmSetup({
          elements,
          confirmParams,
          redirect: 'if_required',
        });
        if (error) {
          return {
            status: 'failed',
            intentId: error.setup_intent?.id ?? '',
            error: error.message ?? 'Could not save your card.',
          };
        }
        return {
          status: mapStripeStatus(setupIntent?.status ?? 'failed'),
          intentId: setupIntent?.id ?? '',
        };
      }

      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams,
        redirect: 'if_required',
      });

      if (error) {
        return {
          status: 'failed',
          intentId: error.payment_intent?.id ?? '',
          error: error.message ?? 'Payment failed.',
        };
      }

      return {
        status: mapStripeStatus(paymentIntent?.status ?? 'failed'),
        intentId: paymentIntent?.id ?? '',
      };
    },

    createSubscription: cfg.createSubscriptionOnBackend
      ? async (input: StartSubscriptionInput): Promise<SubscriptionIntent> => {
          const raw = await cfg.createSubscriptionOnBackend!(input);
          return {
            stripeSubscriptionId: raw.stripe_subscription_id,
            status: raw.status,
            confirmType: raw.confirm_type,
            clientSecret: raw.client_secret,
            provider: 'stripe',
          };
        }
      : undefined,

    createSetupIntent: cfg.createSetupIntentOnBackend
      ? async (input?: SaveCardInput): Promise<SetupIntent> => {
          const raw = await cfg.createSetupIntentOnBackend!(input);
          return {
            id: raw.id,
            clientSecret: raw.client_secret,
            provider: 'stripe',
          };
        }
      : undefined,

    listPaymentMethods: cfg.listPaymentMethodsOnBackend
      ? async (): Promise<SavedCard[]> => {
          const raw = await cfg.listPaymentMethodsOnBackend!();
          return raw.map(mapSavedCard);
        }
      : undefined,

    setDefaultPaymentMethod: cfg.setDefaultPaymentMethodOnBackend
      ? (id: string): Promise<void> => cfg.setDefaultPaymentMethodOnBackend!(id)
      : undefined,

    removePaymentMethod: cfg.removePaymentMethodOnBackend
      ? (id: string): Promise<void> => cfg.removePaymentMethodOnBackend!(id)
      : undefined,

    // No client-side `retrieve`: it needs the client secret, and the webhook
    // is the source of truth anyway. Callers reconcile against backend order
    // status instead. Intentionally omitted (the field is optional).

    listPayments: cfg.listPaymentsOnBackend
      ? (params): Promise<PaymentPage> => cfg.listPaymentsOnBackend!(params)
      : undefined,
  };
}
