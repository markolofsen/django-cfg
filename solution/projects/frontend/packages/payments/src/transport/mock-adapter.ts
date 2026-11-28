// ============================================================================
// @djangocfg/payments — mock adapter (mock-first development)
// ============================================================================
// Fakes the full payment state machine with delays so apps/my can build and
// verify the entire checkout UX before any backend endpoint or Stripe key
// exists. Swapping to the real Stripe adapter is a one-line host change.

import type {
  ConfirmArgs,
  ConfirmResult,
  CreatePaymentInput,
  PaymentIntent,
  PaymentPage,
  PaymentProviderAdapter,
  PaymentRecord,
  SavedCard,
  SaveCardInput,
  SetupIntent,
  StartSubscriptionInput,
  SubscriptionIntent,
} from '../domain/types';

/** Outcome the mock should simulate on confirm. */
export type MockOutcome = 'succeeded' | 'failed' | 'requires_action';

export interface MockAdapterConfig {
  /** Latency per step, ms. Default 600. */
  latencyMs?: number;
  /** What confirm() resolves to. Default 'succeeded'. */
  outcome?: MockOutcome;
  /** Error message when outcome === 'failed'. */
  failureMessage?: string;
  /** Fixture history for listPayments(). */
  history?: PaymentRecord[];
  /**
   * Fixture cards for listPaymentMethods(). Defaults to two: a default Visa
   * and an Amex inside the expiry warning window, so a story renders both the
   * ordinary and the warning row without configuration.
   *
   * Pass `[]` for the loaded-and-empty state. Pass `null` to drop the four
   * card methods entirely — that is the `unavailable` state a host sees when
   * it never wired the endpoints, and it must look different from `[]`.
   */
  cards?: SavedCard[] | null;
  /**
   * Deterministic timestamp factory (tests). Defaults to `new Date()`.
   * Kept injectable so stories/tests stay stable.
   */
  now?: () => Date;
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** A default Visa plus an Amex inside the warning window, relative to `now`. */
function defaultMockCards(now: Date): SavedCard[] {
  const soon = new Date(now.getFullYear(), now.getMonth() + 2, 1);
  return [
    {
      id: 'pm_mock_visa',
      brand: 'visa',
      last4: '4242',
      expMonth: now.getMonth() + 1,
      expYear: now.getFullYear() + 3,
      isDefault: true,
    },
    {
      id: 'pm_mock_amex',
      brand: 'amex',
      last4: '0005',
      expMonth: soon.getMonth() + 1,
      expYear: soon.getFullYear(),
      isDefault: false,
    },
  ];
}

let counter = 0;
function nextId(prefix: string): string {
  counter += 1;
  return `${prefix}_mock_${counter}`;
}

export function createMockPaymentAdapter(
  config: MockAdapterConfig = {},
): PaymentProviderAdapter {
  const {
    latencyMs = 600,
    outcome = 'succeeded',
    failureMessage = 'Your card was declined.',
    history = [],
    now = () => new Date(),
  } = config;

  let lastIntent: PaymentIntent | null = null;

  // `cards: null` means "this adapter has no card-on-file capability", which
  // is expressed by leaving the four methods undefined — not by an empty list.
  const supportsCards = config.cards !== null;
  let cards: SavedCard[] = config.cards ?? defaultMockCards(now());

  return {
    id: 'mock',

    async createIntent(input: CreatePaymentInput): Promise<PaymentIntent> {
      await delay(latencyMs);
      const intent: PaymentIntent = {
        id: nextId('pi'),
        clientSecret: nextId('secret'),
        amount: input.amount,
        currency: input.currency,
        status: 'requires_payment',
        reference: input.reference,
        provider: 'mock',
        createdAt: now().toISOString(),
      };
      lastIntent = intent;
      return intent;
    },

    async confirm(_args: ConfirmArgs): Promise<ConfirmResult> {
      await delay(latencyMs);
      const intentId = lastIntent?.id ?? nextId('pi');

      if (outcome === 'failed') {
        if (lastIntent) lastIntent = { ...lastIntent, status: 'failed' };
        return { status: 'failed', intentId, error: failureMessage };
      }

      if (outcome === 'requires_action') {
        if (lastIntent) lastIntent = { ...lastIntent, status: 'requires_action' };
        return {
          status: 'requires_action',
          intentId,
          nextActionUrl: 'https://mock.test/3ds-challenge',
        };
      }

      if (lastIntent) lastIntent = { ...lastIntent, status: 'succeeded' };
      return { status: 'succeeded', intentId };
    },

    async createSubscription(_input: StartSubscriptionInput): Promise<SubscriptionIntent> {
      await delay(latencyMs);
      const subId = nextId('sub');
      // Mock the deferred flow: a paid first invoice → confirmPayment path, with
      // a fake client_secret the mock confirm() accepts. (Trial/$0 setup path
      // isn't exercised here — Free plans never reach the adapter.)
      const intent: PaymentIntent = {
        id: subId,
        clientSecret: nextId('seti_or_pi_secret'),
        amount: 0,
        currency: 'usd',
        status: 'requires_payment',
        reference: { kind: 'subscription', id: subId },
        provider: 'mock',
        createdAt: now().toISOString(),
      };
      lastIntent = intent;
      return {
        stripeSubscriptionId: subId,
        status: 'incomplete',
        confirmType: 'payment',
        clientSecret: intent.clientSecret,
        provider: 'mock',
      };
    },

    async retrieve(intentId: string): Promise<PaymentIntent> {
      await delay(latencyMs / 2);
      if (lastIntent && lastIntent.id === intentId) return lastIntent;
      return {
        id: intentId,
        clientSecret: null,
        amount: 0,
        currency: 'usd',
        status: 'succeeded',
        reference: { kind: 'order', id: 'unknown' },
        provider: 'mock',
        createdAt: now().toISOString(),
      };
    },

    // Card on file. Defined only when the fixture says this adapter has the
    // capability — `cards: null` leaves all four undefined, which is how a
    // reader tells "unsupported" from "none on file".
    createSetupIntent: supportsCards
      ? async (_input?: SaveCardInput): Promise<SetupIntent> => {
          await delay(latencyMs);
          const id = nextId('seti');
          // Route mock confirm() through the same lastIntent slot the checkout
          // path uses, so `outcome` drives the setup branch identically.
          lastIntent = {
            id,
            clientSecret: nextId('seti_secret'),
            amount: 0,
            currency: 'usd',
            status: 'requires_payment',
            reference: { kind: 'subscription', id },
            provider: 'mock',
            createdAt: now().toISOString(),
          };
          return { id, clientSecret: lastIntent.clientSecret!, provider: 'mock' };
        }
      : undefined,

    listPaymentMethods: supportsCards
      ? async (): Promise<SavedCard[]> => {
          await delay(latencyMs / 2);
          return cards;
        }
      : undefined,

    setDefaultPaymentMethod: supportsCards
      ? async (id: string): Promise<void> => {
          await delay(latencyMs / 2);
          if (!cards.some((card) => card.id === id)) {
            throw new Error(`No such payment method: ${id}`);
          }
          cards = cards.map((card) => ({ ...card, isDefault: card.id === id }));
        }
      : undefined,

    removePaymentMethod: supportsCards
      ? async (id: string): Promise<void> => {
          await delay(latencyMs / 2);
          const target = cards.find((card) => card.id === id);
          if (!target) throw new Error(`No such payment method: ${id}`);
          // Mirrors the server rule: the last card on an active subscription
          // cannot be detached, or the next renewal has nothing to charge.
          if (cards.length === 1) {
            throw new Error('Cannot remove the only card on an active subscription.');
          }
          cards = cards.filter((card) => card.id !== id);
          if (target.isDefault && cards.length > 0) {
            cards = cards.map((card, index) => ({ ...card, isDefault: index === 0 }));
          }
        }
      : undefined,

    async listPayments(): Promise<PaymentPage> {
      await delay(latencyMs / 2);
      return { items: history };
    },
  };
}
