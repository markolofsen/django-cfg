# @djangocfg/payments

Provider-agnostic React payments module. **Stripe-first**, but the package
never depends on a concrete SDK — the host injects an adapter. Battle-tested
in production (one-time PaymentIntent checkout, recurring subscriptions with
Stripe Link, card on file) before extraction into `@djangocfg/*`.

📖 **[Full documentation →](./@docs/README.md)** — architecture, the server
contract, Stripe traps, testing.

## The seam

The host picks **one** adapter and injects it via `<PaymentProvider>`. Package
hooks/components read it through `usePaymentAdapter()` and never import Stripe
or a generated API client directly.

```tsx
import { PaymentProvider, createMockPaymentAdapter } from '@djangocfg/payments';

// Mock-first: build & verify the whole UX before any backend exists.
<PaymentProvider adapter={createMockPaymentAdapter()}>
  {children}
</PaymentProvider>
```

Swapping to real Stripe is a one-line host change:

```tsx
// loadStripe is re-exported by this package — the host never declares @stripe/*.
import { PaymentProvider, createStripeAdapter, loadStripe } from '@djangocfg/payments';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PK!); // once, module scope
const adapter = createStripeAdapter({
  getStripe: () => stripePromise,
  createIntentOnBackend: (input) => api.payments.createIntent(input), // host transport
});

<PaymentProvider adapter={adapter}>{children}</PaymentProvider>;
```

## Layering

```
domain/      pure types + money/card helpers   (no React, no Stripe)
context/     <PaymentProvider> + <CheckoutGuard>   (the seam, the in-flight lock)
transport/   mock-adapter | stripe-adapter      (the SDK seam; see the note below)
hooks/       useCheckout, useCardSetup, usePaymentHistory, useSavedCards
components/  CheckoutForm, CardSetupForm, StripePaymentElement, dialogs, tables, badges
```

`@stripe/*` is a **runtime** dependency of exactly two files
(`transport/stripe-adapter.ts`, `components/StripePaymentElement.tsx`) and a
**type-only** one of a third (`components/appearance.ts`) — enforced by
`scripts/check-stripe-imports.mjs`, which `pnpm check` runs.
`@stripe/stripe-js` is only the tiny CDN loader (the real SDK loads from
js.stripe.com at runtime), so tree-shaking drops the Stripe components from
mock-only bundles. See [`@docs/ARCHITECTURE.md`](./@docs/ARCHITECTURE.md) for
why this is one package and where the boundaries are.

## Styles (Tailwind v4) — required wiring

This package is consumed **from source** and styled with Tailwind utility
classes. Tailwind v4 only generates classes it can see, so the consumer's
global CSS must import the package's styles entry (it carries the `@source`
directive that points Tailwind at this package's sources):

```css
/* your app's globals.css */
@import "@djangocfg/ui-core/styles/full";
@import "@djangocfg/payments/styles";   /* ← add this */
```

Symptom when missing: components render unstyled in spots — e.g.
`PaymentStatusBadge` chips lose their background tint and show as plain text.
Next.js hosts also add the package to `transpilePackages`.

## Public API

| Export | Kind | Purpose |
|---|---|---|
| `PaymentProvider` / `usePaymentAdapter` | context | inject / read the adapter |
| `createMockPaymentAdapter` | adapter | full fake state machine (success / declined / 3DS / cards) |
| `createStripeAdapter` | adapter | real Stripe (host supplies key + backend calls) |
| `useCheckout` | hook | `idle → creating → requires_payment → processing → succeeded\|failed\|requires_action` |
| `useCardSetup` | hook | the same machine for saving a card with no charge |
| `useSavedCards` | hook | cards on file as a phase (`unavailable\|loading\|ready\|error`) + set-default / remove |
| `usePaymentHistory` | hook | paginated history via `adapter.listPayments` |
| `CheckoutDialog` | component | close-locked dialog shell; wrap your checkout body in it |
| `CheckoutForm` | component | provider-agnostic form shell; inject the field via `paymentField` |
| `CardSetupForm` | component | the same, for saving a card (no amount, no "Paid") |
| `UpdateCardDialog` | component | the whole add-a-card flow: intent on open, confirm, report |
| `SavedCardList` | component | cards table: default badge, expiry warning, row actions |
| `StripePaymentElement` | component | `<Elements>` + `<PaymentElement>`; render-props the live Elements |
| `PaymentHistory` | component | sortable table of `PaymentRecord` |
| `PaymentStatusBadge` | component | status pill on ui-core semantic tokens |
| `toMinorUnits` / `toMajorUnits` / `formatAmount` | util | money at the boundary (integer minor units) |
| `cardExpiresAt` / `isCardExpired` / `isCardExpiringSoon` / `formatCardExpiry` / `sortCards` / `cardsOf` | util | card derivations against a clock |

## Conventions

- Source-consumed (no bundler); `main`/`types`/`exports` → `./src/index.ts`.
- ui-core flat import. No widget dependency: a package may not depend on a
  widget (`widgets/CLAUDE.md`).
- Does **not** mount its own `<UiProviders>` — the host provides it once.
- Locale-free: user-facing labels are props/slots (host supplies i18n).
- Verify with `pnpm -F @djangocfg/payments check` and `… lint`.

## Card on file

A subscription outlives the card that pays for it: when a renewal fails Stripe
retries for ~2 weeks **against the same stored card**, then gives up. Without
a way to replace it, a customer who wanted to pay loses the subscription.

```tsx
const { phase, canAddCard, canManageCards, refresh, setDefault, remove, isBusy } =
  useSavedCards();

<SavedCardList
  phase={phase}
  busy={isBusy}
  onAddCard={canAddCard ? () => setOpen(true) : undefined}
  onSetDefault={canManageCards ? setDefault : undefined}
  onRemove={canManageCards ? remove : undefined}
/>
<UpdateCardDialog open={open} onClose={close} onSaved={() => { close(); void refresh(); }} />
```

Four host endpoints, wired all-or-none, plus four server rules that fail
silently — see [`@docs/CARD_ON_FILE.md`](./@docs/CARD_ON_FILE.md) and
[`@docs/SERVER_CONTRACT.md`](./@docs/SERVER_CONTRACT.md).

> **Not Link, not the Billing Portal.** Link is a buyer-side wallet —
> `link.com` does not know your subscription exists, and a renewal charges the
> stored `pm_…`. The Billing Portal is a server-side redirect that discards
> this package's theming and the host's locale. Reasoning in
> [`@docs/STRIPE_NOTES.md`](./@docs/STRIPE_NOTES.md).

## Configuration & keys

Three Stripe keys, split by where they're safe to live. Stripe ships **test**
(`sk_test_…`, `pk_test_…`) and **live** (`sk_live_…`, `pk_live_…`) flavours
with the **same variable names**; only the values differ. Bring up test first.

| Key | Prefix | Lives in | Exposed to browser? |
|---|---|---|---|
| Secret key | `sk_test_…` / `sk_live_…` | **Backend only** (`STRIPE__SECRET_KEY`) | ❌ never |
| Webhook signing secret | `whsec_…` | **Backend only** (`STRIPE__WEBHOOK_SECRET`) | ❌ never |
| Publishable key | `pk_test_…` / `pk_live_…` | Backend + Frontend | ✅ safe (public by design) |

```dotenv
# backend, git-ignored secrets file
STRIPE__SECRET_KEY=sk_test_xxx
STRIPE__PUBLISHABLE_KEY=pk_test_xxx
STRIPE__WEBHOOK_SECRET=whsec_xxx          # comma-separate to rotate: whsec_new,whsec_old

# your Next.js app .env
NEXT_PUBLIC_STRIPE_PK=pk_test_xxx
```

With **no** `NEXT_PUBLIC_STRIPE_PK` set, the host falls back to the **mock
adapter** — the whole UX still renders (no real charge).

> ⚠️ The secret (`sk_`) and webhook (`whsec_`) keys must live in a git-ignored
> file or a secret manager. Only `pk_…` is safe in tracked config.

## Stripe setup (test mode)

1. **Test keys** — Dashboard → Developers → API keys (toggle "test mode").
2. **Webhook** — locally, the Stripe CLI prints a `whsec_…` for the forwarded
   endpoint:
   ```bash
   stripe listen --forward-to localhost:8000/<your-webhook-path>/
   ```
   Deployed: create the endpoint in the Dashboard and subscribe to
   `payment_intent.succeeded`, `payment_intent.payment_failed`,
   `charge.refunded` (plus the invoice/subscription events your dunning needs).
3. **Test a payment** — card `4242 4242 4242 4242`, any future expiry/CVC.
   ```bash
   stripe trigger payment_intent.succeeded
   stripe events resend <evt_id>   # test idempotency / replay
   ```

## Going live

1. Switch all three `STRIPE__*` values and `NEXT_PUBLIC_STRIPE_PK` to live.
2. Create a **live** webhook endpoint (live mode has its own signing secret).
3. Register your domain for Apple Pay / Google Pay if you enable wallets.
4. Do a small real charge to confirm end-to-end.
