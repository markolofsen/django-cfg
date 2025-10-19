import * as Models from "./models";


/**
 * API endpoints for Trading.
 */
export class TradingTrading {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async ordersList(page?: number, page_size?: number): Promise<Models.PaginatedOrderList>;
  async ordersList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedOrderList>;

  /**
   * List orders
   * 
   * ViewSet for trading orders.
   */
  async ordersList(...args: any[]): Promise<Models.PaginatedOrderList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/api/trading/orders/", { params });
    return response;
  }

  /**
   * Create order
   * 
   * ViewSet for trading orders.
   */
  async ordersCreate(data: Models.OrderCreateRequest): Promise<Models.OrderCreate> {
    const response = await this.client.request('POST', "/api/trading/orders/", { body: data });
    return response;
  }

  /**
   * Get order
   * 
   * ViewSet for trading orders.
   */
  async ordersRetrieve(id: number): Promise<Models.Order> {
    const response = await this.client.request('GET', `/api/trading/orders/${id}/`);
    return response;
  }

  /**
   * ViewSet for trading orders.
   */
  async ordersUpdate(id: number, data: Models.OrderRequest): Promise<Models.Order> {
    const response = await this.client.request('PUT', `/api/trading/orders/${id}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for trading orders.
   */
  async ordersPartialUpdate(id: number, data?: Models.PatchedOrderRequest): Promise<Models.Order> {
    const response = await this.client.request('PATCH', `/api/trading/orders/${id}/`, { body: data });
    return response;
  }

  /**
   * ViewSet for trading orders.
   */
  async ordersDestroy(id: number): Promise<void> {
    const response = await this.client.request('DELETE', `/api/trading/orders/${id}/`);
    return;
  }

  async portfoliosList(page?: number, page_size?: number): Promise<Models.PaginatedPortfolioList>;
  async portfoliosList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedPortfolioList>;

  /**
   * List portfolios
   * 
   * ViewSet for trading portfolios.
   */
  async portfoliosList(...args: any[]): Promise<Models.PaginatedPortfolioList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/api/trading/portfolios/", { params });
    return response;
  }

  /**
   * Get portfolio
   * 
   * ViewSet for trading portfolios.
   */
  async portfoliosRetrieve(id: number): Promise<Models.Portfolio> {
    const response = await this.client.request('GET', `/api/trading/portfolios/${id}/`);
    return response;
  }

  /**
   * Get my portfolio
   * 
   * Get current user's portfolio.
   */
  async portfoliosMeRetrieve(): Promise<Models.Portfolio> {
    const response = await this.client.request('GET', "/api/trading/portfolios/me/");
    return response;
  }

  /**
   * Get portfolio statistics
   * 
   * Get portfolio statistics.
   */
  async portfoliosStatsRetrieve(): Promise<Models.PortfolioStats> {
    const response = await this.client.request('GET', "/api/trading/portfolios/stats/");
    return response;
  }

}