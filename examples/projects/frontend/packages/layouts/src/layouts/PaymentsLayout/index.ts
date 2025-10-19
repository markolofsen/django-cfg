/**
 * Payments Layout (v2.0 - Simplified)
 *
 * Exports:
 * - PaymentsLayout: Main layout component
 * - PaymentTab: Tab type definition
 * - Payment events: openCreatePaymentDialog, openPaymentDetailsDialog, closePaymentsDialog
 */

export { PaymentsLayout } from './PaymentsLayout';
export type { PaymentTab } from './types';
export {
  openCreatePaymentDialog,
  openPaymentDetailsDialog,
  closePaymentsDialog
} from './events';
