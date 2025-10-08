import * as Models from "./models";


/**
 * API endpoints for Shop - Orders.
 */
export class ShopOrdersAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(customer?: number, ordering?: string, page?: number, page_size?: number, search?: string, status?: string): Promise<Models.PaginatedOrderListList[]>;
  async list(params?: { customer?: number; ordering?: string; page?: number; page_size?: number; search?: string; status?: string }): Promise<Models.PaginatedOrderListList[]>;

  /**
   * List orders
   * 
   * Get a list of orders (admin only)
   */
  async list(...args: any[]): Promise<Models.PaginatedOrderListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { customer: args[0], ordering: args[1], page: args[2], page_size: args[3], search: args[4], status: args[5] };
    }
    const response = await this.client.request('GET', "/shop/orders/", { params });
    return (response as any).results || [];
  }

  /**
   * Get order
   * 
   * Get details of a specific order
   */
  async retrieve(id: number): Promise<Models.OrderDetail> {
    const response = await this.client.request('GET', `/shop/orders/${id}/`);
    return response;
  }

}