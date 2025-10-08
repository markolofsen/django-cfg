import * as Models from "./models";


/**
 * API endpoints for Shop - Products.
 */
export class ShopProductsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List products
 * 
 * Get a paginated list of products
 */
async list(category?: number | null, is_digital?: boolean | null, is_featured?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null, status?: string | null): Promise<Models.PaginatedProductListList[]> {
  const response = await this.client.request<Models.PaginatedProductListList[]>('GET', "/shop/products/", { params: { category, is_digital, is_featured, ordering, page, page_size, search, status } });
  return (response as any).results || [];
}

  /**
 * Get product
 * 
 * Get detailed information about a specific product
 */
async retrieve(slug: string): Promise<Models.ProductDetail> {
  const response = await this.client.request<Models.ProductDetail>('GET', `/shop/products/${slug}/`);
  return response;
}

  /**
 * Get featured products
 * 
 * Get featured products
 */
async featuredRetrieve(): Promise<Models.ProductDetail> {
  const response = await this.client.request<Models.ProductDetail>('GET', "/shop/products/featured/");
  return response;
}

  /**
 * Get shop statistics
 * 
 * Get comprehensive shop statistics
 */
async statsRetrieve(): Promise<Models.ShopStats> {
  const response = await this.client.request<Models.ShopStats>('GET', "/shop/products/stats/");
  return response;
}

}