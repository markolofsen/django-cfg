/**
 * Payment Events System (v2.0 - Simplified)
 *
 * Event-based communication for dialogs using DOM events
 * Removed: API Keys events (deprecated)
 */

// ─────────────────────────────────────────────────────────────────────────
// Event Names
// ─────────────────────────────────────────────────────────────────────────

export const PAYMENT_EVENTS = {
  OPEN_CREATE_PAYMENT_DIALOG: 'payments:open-create-payment',
  OPEN_PAYMENT_DETAILS_DIALOG: 'payments:open-payment-details',
  CLOSE_DIALOG: 'payments:close-dialog',
} as const;

// ─────────────────────────────────────────────────────────────────────────
// Event Types
// ─────────────────────────────────────────────────────────────────────────

export type PaymentEvent =
  | { type: 'OPEN_CREATE_PAYMENT' }
  | { type: 'OPEN_PAYMENT_DETAILS'; id: string }
  | { type: 'CLOSE_DIALOG' };

// ─────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────

export const openCreatePaymentDialog = () => {
  window.dispatchEvent(new Event(PAYMENT_EVENTS.OPEN_CREATE_PAYMENT_DIALOG));
};

export const openPaymentDetailsDialog = (id: string) => {
  window.dispatchEvent(
    new CustomEvent(PAYMENT_EVENTS.OPEN_PAYMENT_DETAILS_DIALOG, {
      detail: { id },
    })
  );
};

export const closePaymentsDialog = () => {
  window.dispatchEvent(new Event(PAYMENT_EVENTS.CLOSE_DIALOG));
};
