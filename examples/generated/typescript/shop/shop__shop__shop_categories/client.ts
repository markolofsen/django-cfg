import * as Models from "./models";


/**
 * API endpoints for Shop - Categories.
 */
export class ShopCategoriesAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedShopCategoryList[]>;
  async list(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedShopCategoryList[]>;

  /**
   * List categories
   * 
   * Get a list of all shop categories
   */
  async list(...args: any[]): Promise<Models.PaginatedShopCategoryList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/shop/categories/", { params });
    return (response as any).results || [];
  }

  /**
   * Get category
   * 
   * Get details of a specific category
   */
  async retrieve(slug: string): Promise<Models.ShopCategory> {
    const response = await this.client.request('GET', `/shop/categories/${slug}/`);
    return response;
  }

}