import * as Models from "./models";


/**
 * API endpoints for Shop - Orders.
 */
export class ShopOrdersAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List orders
 * 
 * Get a list of orders (admin only)
 */
async list(customer?: number | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null, status?: string | null): Promise<Models.PaginatedOrderListList[]> {
  const response = await this.client.request<Models.PaginatedOrderListList[]>('GET', "/shop/orders/", { params: { customer, ordering, page, page_size, search, status } });
  return (response as any).results || [];
}

  /**
 * Get order
 * 
 * Get details of a specific order
 */
async retrieve(id: number): Promise<Models.OrderDetail> {
  const response = await this.client.request<Models.OrderDetail>('GET', `/shop/orders/${id}/`);
  return response;
}

}