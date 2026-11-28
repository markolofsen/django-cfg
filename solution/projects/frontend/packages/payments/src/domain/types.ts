// ============================================================================
// @djangocfg/payments — domain types (framework-free: no React, no Stripe)
// ============================================================================
// This is the stable contract the host app compiles against. Package code
// depends on these types and the PaymentProviderAdapter seam — never on a
// concrete SDK or a generated API client.

/** ISO 4217 currency, lowercase (e.g. 'usd'). */
export type Currency = string;

/** Amount in the smallest unit of the currency (e.g. cents for USD). */
export type MinorUnits = number;

/** Provider identifier. `(string & {})` keeps the union open for future providers. */
export type PaymentProviderId = 'stripe' | 'mock' | (string & {});

/** What an app entity a payment settles. */
export interface PaymentReference {
  kind: 'order' | 'subscription' | 'addon';
  id: string;
}

/**
 * The checkout state machine. Shared by `useCheckout` and the mock adapter so
 * the whole UX can be exercised before any provider exists.
 */
export type PaymentStatus =
  | 'idle'
  | 'creating' // creating the PaymentIntent on the backend
  | 'requires_payment' // client_secret ready, awaiting payment details
  | 'processing' // confirming with the provider
  | 'requires_action' // 3DS / redirect needed
  | 'succeeded'
  | 'failed'
  | 'canceled';

/** A payment in flight or settled. Mirrors a provider intent, normalized. */
export interface PaymentIntent {
  /** Provider intent id (e.g. `pi_…` for Stripe). */
  id: string;
  /** Provider client secret used to confirm on the frontend (Stripe Elements). */
  clientSecret: string | null;
  amount: MinorUnits;
  currency: Currency;
  status: PaymentStatus;
  reference: PaymentReference;
  provider: PaymentProviderId;
  /** ISO timestamp. */
  createdAt: string;
}

/** Input to create a payment intent. Amount is authoritative server-side. */
export interface CreatePaymentInput {
  amount: MinorUnits;
  currency: Currency;
  reference: PaymentReference;
  /** Provider-specific extras (coupon, save card, return_url…). */
  metadata?: Record<string, string>;
}

/** Result of confirming a payment on the frontend. */
export interface ConfirmResult {
  status: PaymentStatus;
  intentId: string;
  error?: string;
  /** Set when the provider needs a redirect / 3DS step. */
  nextActionUrl?: string;
}

/** A historical payment row for <PaymentHistory>. */
export interface PaymentRecord {
  id: string;
  amount: MinorUnits;
  currency: Currency;
  status: PaymentStatus;
  reference: PaymentReference;
  provider: PaymentProviderId;
  createdAt: string;
}

/** Page of payment records. */
export interface PaymentPage {
  items: PaymentRecord[];
  nextCursor?: string;
}

/**
 * Which client-side confirm to run (deferred subscription flow). For a one-time
 * PaymentIntent this is always `'payment'` (the default). For a subscription it
 * comes from the backend: `'payment'` when a first invoice is due
 * (`stripe.confirmPayment`), `'setup'` for a $0/trial card-on-file
 * (`stripe.confirmSetup`).
 */
export type ConfirmType = 'payment' | 'setup';

/** Arguments for the adapter's confirm step. */
export interface ConfirmArgs {
  clientSecret: string;
  /** Provider-native confirm payload, e.g. a Stripe Elements instance. */
  elementsContext?: unknown;
  returnUrl?: string;
  /** Dispatch confirmPayment vs confirmSetup. Default `'payment'`. */
  confirmType?: ConfirmType;
}

/** Input to start a subscription checkout (deferred flow). */
export interface StartSubscriptionInput {
  plan: string;
  cycle: 'monthly' | 'annual' | (string & {});
  /** Prefill for Stripe Link / receipt. */
  email?: string;
}

/**
 * The backend's deferred-subscription handle, normalized. The subscription is
 * created `incomplete`; the client confirms `clientSecret` with the call named
 * by `confirmType`. `clientSecret` is null only when there is nothing to
 * confirm (a Free plan subscribed directly — the host handles that BEFORE
 * calling the adapter, so in practice the adapter always gets a secret).
 */
export interface SubscriptionIntent {
  stripeSubscriptionId: string;
  status: string;
  confirmType: ConfirmType;
  clientSecret: string | null;
  provider: PaymentProviderId;
}

// ---------------------------------------------------------------------------
// Card on file
// ---------------------------------------------------------------------------
// A subscription outlives the card that pays for it. Stripe retries a failed
// renewal for ~2 weeks against the SAME stored card, so a customer who cannot
// replace it loses the subscription regardless of intent to pay.
//
// Saving a card here is the same Stripe operation as the $0/trial branch of
// checkout — a SetupIntent confirmed with `confirmSetup`. Only the entry point
// is new; `ConfirmArgs.confirmType = 'setup'` already dispatches it.

/** A SetupIntent: authorization to store a card, charging nothing now. */
export interface SetupIntent {
  /** Provider intent id (e.g. `seti_…` for Stripe). */
  id: string;
  /** Confirmed on the frontend with `confirmType: 'setup'`. */
  clientSecret: string;
  provider: PaymentProviderId;
}

/** Input to create a SetupIntent. */
export interface SaveCardInput {
  /**
   * Make the saved card this subscription's default on success. Omit to store
   * it at account level only. The CUSTOMER is always resolved server-side from
   * the session — never sent from here.
   */
  subscriptionId?: string;
}

/**
 * A card already on file.
 *
 * Carries no `status` and no `isExpiring` on purpose: both are derivations
 * from `expMonth`/`expYear` against today, and a stored copy goes stale on the
 * first day of a month. Readers derive them.
 */
export interface SavedCard {
  /** Provider payment-method id (e.g. `pm_…`). */
  id: string;
  /** Display only — never branch on it. */
  brand: string;
  last4: string;
  /** 1-12. */
  expMonth: number;
  /** Four digits. */
  expYear: number;
  /** Whether renewals charge this card. */
  isDefault: boolean;
}

/**
 * Cards on file as a phase, not a boolean pair.
 *
 * `[]` answers three different questions identically: the host wired no card
 * endpoints, the read has not run, and the customer genuinely has no card.
 * They are three screens, so they are three states.
 */
export type SavedCardsPhase =
  /** The adapter defines no card methods — no card-on-file capability here. */
  | { kind: 'unavailable' }
  /** Never loaded. A reserved-height skeleton, not nothing. */
  | { kind: 'loading' }
  | { kind: 'ready'; cards: SavedCard[]; refreshing: boolean }
  /** `previous` keeps the last known list, so a failed refresh does not blank it. */
  | { kind: 'error'; message: string; previous?: SavedCard[] };

/**
 * Provider-agnostic seam. The HOST injects one implementation via
 * <PaymentProvider adapter={…}>. Package code depends on THIS interface,
 * never on a concrete SDK or a generated client.
 */
export interface PaymentProviderAdapter {
  readonly id: PaymentProviderId;
  /** Backend creates the intent; returns a client_secret to confirm with. */
  createIntent(input: CreatePaymentInput): Promise<PaymentIntent>;
  /**
   * Confirm the intent on the frontend. Dispatches on `args.confirmType`:
   * `'payment'` → `stripe.confirmPayment`, `'setup'` → `stripe.confirmSetup`.
   */
  confirm(args: ConfirmArgs): Promise<ConfirmResult>;
  /**
   * Optional (subscription providers): backend creates an `incomplete` Stripe
   * subscription (deferred flow) and returns a `clientSecret` + `confirmType`.
   * Absent on the mock/one-time-only adapters.
   */
  createSubscription?(input: StartSubscriptionInput): Promise<SubscriptionIntent>;
  /** Optional: poll/retrieve status after a redirect. */
  retrieve?(intentId: string): Promise<PaymentIntent>;
  /** Optional: paginated history for <PaymentHistory>. */
  listPayments?(params?: { limit?: number; cursor?: string }): Promise<PaymentPage>;

  // --- Card on file (all four optional together) ---------------------------
  // ABSENCE IS THE SIGNAL. A one-time-payment adapter has no card on file, and
  // an undefined method — not a capability flag — is what says so. Readers
  // MUST render an `unavailable` state rather than coercing to an empty list:
  // "no cards on file" and "this host never wired the endpoint" look identical
  // once both are `[]`, and they mean opposite things.

  /** Backend creates a SetupIntent against the stored customer. */
  createSetupIntent?(input?: SaveCardInput): Promise<SetupIntent>;
  /** Cards on file, newest default first. */
  listPaymentMethods?(): Promise<SavedCard[]>;
  /** Make one saved card the default for renewals. */
  setDefaultPaymentMethod?(id: string): Promise<void>;
  /** Detach a saved card. Rejected server-side when it is the last one on an active subscription. */
  removePaymentMethod?(id: string): Promise<void>;
}
