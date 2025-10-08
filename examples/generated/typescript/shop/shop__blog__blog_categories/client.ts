import * as Models from "./models";


/**
 * API endpoints for Blog - Categories.
 */
export class ShopBlogCategoriesAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedBlogCategoryList[]>;
  async list(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedBlogCategoryList[]>;

  /**
   * List categories
   * 
   * Get a list of all blog categories
   */
  async list(...args: any[]): Promise<Models.PaginatedBlogCategoryList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/blog/categories/", { params });
    return (response as any).results || [];
  }

  /**
   * Create category
   * 
   * Create a new blog category
   */
  async create(data: Models.BlogCategoryRequest): Promise<Models.BlogCategory> {
    const response = await this.client.request('POST', "/blog/categories/", { body: data });
    return response;
  }

  /**
   * Get category
   * 
   * Get details of a specific category
   */
  async retrieve(slug: string): Promise<Models.BlogCategory> {
    const response = await this.client.request('GET', `/blog/categories/${slug}/`);
    return response;
  }

  /**
   * Update category
   * 
   * Update category information
   */
  async update(slug: string, data: Models.BlogCategoryRequest): Promise<Models.BlogCategory> {
    const response = await this.client.request('PUT', `/blog/categories/${slug}/`, { body: data });
    return response;
  }

  /**
   * Delete category
   * 
   * Delete a category
   */
  async destroy(slug: string): Promise<void> {
    const response = await this.client.request('DELETE', `/blog/categories/${slug}/`);
    return;
  }

}