import * as Models from "./models";


/**
 * API endpoints for Payments.
 */
export class CfgPayments {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get user balance
   * 
   * Get current user balance and transaction statistics
   */
  async balanceRetrieve(): Promise<Models.Balance> {
    const response = await this.client.request('GET', "/cfg/payments/balance/");
    return response;
  }

  /**
   * Get available currencies
   * 
   * Returns list of available currencies with token+network info
   */
  async currenciesList(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/payments/currencies/");
    return response;
  }

  async paymentsList(page?: number, page_size?: number): Promise<Models.PaginatedPaymentListList>;
  async paymentsList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedPaymentListList>;

  /**
   * ViewSet for payment operations. Endpoints: - GET /payments/ - List
   * user's payments - GET /payments/{id}/ - Get payment details - POST
   * /payments/create/ - Create new payment - GET /payments/{id}/status/ -
   * Check payment status - POST /payments/{id}/confirm/ - Confirm payment
   */
  async paymentsList(...args: any[]): Promise<Models.PaginatedPaymentListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/payments/payments/", { params });
    return response;
  }

  /**
   * ViewSet for payment operations. Endpoints: - GET /payments/ - List
   * user's payments - GET /payments/{id}/ - Get payment details - POST
   * /payments/create/ - Create new payment - GET /payments/{id}/status/ -
   * Check payment status - POST /payments/{id}/confirm/ - Confirm payment
   */
  async paymentsRetrieve(id: string): Promise<Models.PaymentDetail> {
    const response = await this.client.request('GET', `/cfg/payments/payments/${id}/`);
    return response;
  }

  /**
   * POST /api/v1/payments/{id}/confirm/ Confirm payment (user clicked "I
   * have paid"). Checks status with provider and creates transaction if
   * completed.
   */
  async paymentsConfirmCreate(id: string): Promise<Models.PaymentList> {
    const response = await this.client.request('POST', `/cfg/payments/payments/${id}/confirm/`);
    return response;
  }

  /**
   * GET /api/v1/payments/{id}/status/?refresh=true Check payment status
   * (with optional refresh from provider). Query params: - refresh: boolean
   * (default: false) - Force refresh from provider
   */
  async paymentsStatusRetrieve(id: string): Promise<Models.PaymentList[]> {
    const response = await this.client.request('GET', `/cfg/payments/payments/${id}/status/`);
    return (response as any).results || [];
  }

  /**
   * POST /api/v1/payments/create/ Create new payment. Request body: {
   * "amount_usd": "100.00", "currency_code": "USDTTRC20", "description":
   * "Optional description" }
   */
  async paymentsCreateCreate(): Promise<Models.PaymentList> {
    const response = await this.client.request('POST', "/cfg/payments/payments/create/");
    return response;
  }

  async transactionsList(limit?: number, offset?: number, type?: string): Promise<any>;
  async transactionsList(params?: { limit?: number; offset?: number; type?: string }): Promise<any>;

  /**
   * Get user transactions
   * 
   * Get user transactions with pagination and filtering
   */
  async transactionsList(...args: any[]): Promise<any> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { limit: args[0], offset: args[1], type: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/payments/transactions/", { params });
    return response;
  }

}