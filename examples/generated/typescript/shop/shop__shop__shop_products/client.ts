import * as Models from "./models";


/**
 * API endpoints for Shop - Products.
 */
export class ShopProductsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(category?: number, is_digital?: boolean, is_featured?: boolean, ordering?: string, page?: number, page_size?: number, search?: string, status?: string): Promise<Models.PaginatedProductListList[]>;
  async list(params?: { category?: number; is_digital?: boolean; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string }): Promise<Models.PaginatedProductListList[]>;

  /**
   * List products
   * 
   * Get a paginated list of products
   */
  async list(...args: any[]): Promise<Models.PaginatedProductListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { category: args[0], is_digital: args[1], is_featured: args[2], ordering: args[3], page: args[4], page_size: args[5], search: args[6], status: args[7] };
    }
    const response = await this.client.request('GET', "/shop/products/", { params });
    return (response as any).results || [];
  }

  /**
   * Get product
   * 
   * Get detailed information about a specific product
   */
  async retrieve(slug: string): Promise<Models.ProductDetail> {
    const response = await this.client.request('GET', `/shop/products/${slug}/`);
    return response;
  }

  /**
   * Get featured products
   * 
   * Get featured products
   */
  async featuredRetrieve(): Promise<Models.ProductDetail> {
    const response = await this.client.request('GET', "/shop/products/featured/");
    return response;
  }

  /**
   * Get shop statistics
   * 
   * Get comprehensive shop statistics
   */
  async statsRetrieve(): Promise<Models.ShopStats> {
    const response = await this.client.request('GET', "/shop/products/stats/");
    return response;
  }

}