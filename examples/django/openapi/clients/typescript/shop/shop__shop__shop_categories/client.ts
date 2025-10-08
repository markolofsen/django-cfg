import * as Models from "./models";


/**
 * API endpoints for Shop - Categories.
 */
export class ShopCategoriesAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List categories
 * 
 * Get a list of all shop categories
 */
async list(ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null): Promise<Models.PaginatedShopCategoryList[]> {
  const response = await this.client.request<Models.PaginatedShopCategoryList[]>('GET', "/shop/categories/", { params: { ordering, page, page_size, search } });
  return (response as any).results || [];
}

  /**
 * Get category
 * 
 * Get details of a specific category
 */
async retrieve(slug: string): Promise<Models.ShopCategory> {
  const response = await this.client.request<Models.ShopCategory>('GET', `/shop/categories/${slug}/`);
  return response;
}

}