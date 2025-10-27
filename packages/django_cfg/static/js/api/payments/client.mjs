import { BaseAPIClient } from '../base.mjs';

/**
 * Payments API Client
 * Auto-generated from OpenAPI schema
 * @module payments
 * @extends BaseAPIClient
 */
export class PaymentsAPI extends BaseAPIClient {
    /**
     * Initialize payments API client
     * @param {string} [baseURL] - Optional base URL
     */
    constructor(baseURL) {
        super(baseURL);
    }

    /**
     * Get user balance     * Get current user balance and transaction statistics     * @returns {Promise<Balance>} Response data
     */
    async paymentsBalanceRetrieve() {
        const path = `/cfg/payments/balance/`;        return this.get(path);    }
    /**
     * Get available currencies     * Returns list of available currencies with token+network info     * @returns {Promise<Currency[]>} Response data
     */
    async paymentsCurrenciesList() {
        const path = `/cfg/payments/currencies/`;        return this.get(path);    }
    /**
     * paymentsPaymentsList     * ViewSet for payment operations.

Endpoints:
- GET /payments/ - List user's payments
- GET /payments/{id}/ - Get payment details
- POST /payments/create/ - Create new payment
- GET /payments/{id}/status/ - Check payment status
- POST /payments/{id}/confirm/ - Confirm payment     * @param {Object} [params={}] - Query parameters     * @param {number} [params.page] - A page number within the paginated result set.     * @param {number} [params.page_size] - Number of results to return per page.     * @returns {Promise<PaginatedPaymentListList>} Response data
     */
    async paymentsPaymentsList(params = {}) {
        const path = `/cfg/payments/payments/`;        return this.get(path, params);    }
    /**
     * paymentsPaymentsRetrieve     * ViewSet for payment operations.

Endpoints:
- GET /payments/ - List user's payments
- GET /payments/{id}/ - Get payment details
- POST /payments/create/ - Create new payment
- GET /payments/{id}/status/ - Check payment status
- POST /payments/{id}/confirm/ - Confirm payment     * @param {string} id     * @returns {Promise<PaymentDetail>} Response data
     */
    async paymentsPaymentsRetrieve(id) {
        const path = `/cfg/payments/payments/${id}/`;        return this.get(path);    }
    /**
     * paymentsPaymentsConfirmCreate     * POST /api/v1/payments/{id}/confirm/

Confirm payment (user clicked "I have paid").
Checks status with provider and creates transaction if completed.     * @param {string} id     * @returns {Promise<PaymentList>} Response data
     */
    async paymentsPaymentsConfirmCreate(id) {
        const path = `/cfg/payments/payments/${id}/confirm/`;        return this.post(path, {});    }
    /**
     * paymentsPaymentsStatusRetrieve     * GET /api/v1/payments/{id}/status/?refresh=true

Check payment status (with optional refresh from provider).

Query params:
- refresh: boolean (default: false) - Force refresh from provider     * @param {string} id     * @returns {Promise<PaymentList>} Response data
     */
    async paymentsPaymentsStatusRetrieve(id) {
        const path = `/cfg/payments/payments/${id}/status/`;        return this.get(path);    }
    /**
     * paymentsPaymentsCreateCreate     * POST /api/v1/payments/create/

Create new payment.

Request body:
{
    "amount_usd": "100.00",
    "currency_code": "USDTTRC20",
    "description": "Optional description"
}     * @returns {Promise<PaymentList>} Response data
     */
    async paymentsPaymentsCreateCreate() {
        const path = `/cfg/payments/payments/create/`;        return this.post(path, {});    }
    /**
     * Get user transactions     * Get user transactions with pagination and filtering     * @param {Object} [params={}] - Query parameters     * @param {number} [params.limit] - Number of transactions to return (max 100)     * @param {number} [params.offset] - Offset for pagination     * @param {string} [params.type] - Filter by transaction type (deposit/withdrawal)     * @returns {Promise<Transaction[]>} Response data
     */
    async paymentsTransactionsList(params = {}) {
        const path = `/cfg/payments/transactions/`;        return this.get(path, params);    }
}

// Default instance for convenience
export const paymentsAPI = new PaymentsAPI();

// Default export
export default PaymentsAPI;