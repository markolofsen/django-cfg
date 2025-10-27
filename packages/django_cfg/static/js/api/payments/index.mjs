/**
 * Payments API Module
 * Re-exports the API client for convenient importing
 * @module payments
 */

import { PaymentsAPI, paymentsAPI } from './client.mjs';

// Re-export the class and instance
export { PaymentsAPI, paymentsAPI };

// Default export is the instance for convenience
export default paymentsAPI;