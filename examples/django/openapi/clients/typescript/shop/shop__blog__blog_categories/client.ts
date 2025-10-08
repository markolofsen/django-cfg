import * as Models from "./models";


/**
 * API endpoints for Blog - Categories.
 */
export class ShopBlogCategoriesAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List categories
 * 
 * Get a list of all blog categories
 */
async list(ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null): Promise<Models.PaginatedBlogCategoryList[]> {
  const response = await this.client.request<Models.PaginatedBlogCategoryList[]>('GET', "/blog/categories/", { params: { ordering, page, page_size, search } });
  return (response as any).results || [];
}

  /**
 * Create category
 * 
 * Create a new blog category
 */
async create(data: Models.BlogCategoryRequest): Promise<Models.BlogCategory> {
  const response = await this.client.request<Models.BlogCategory>('POST', "/blog/categories/", { body: data });
  return response;
}

  /**
 * Get category
 * 
 * Get details of a specific category
 */
async retrieve(slug: string): Promise<Models.BlogCategory> {
  const response = await this.client.request<Models.BlogCategory>('GET', `/blog/categories/${slug}/`);
  return response;
}

  /**
 * Update category
 * 
 * Update category information
 */
async update(slug: string, data: Models.BlogCategoryRequest): Promise<Models.BlogCategory> {
  const response = await this.client.request<Models.BlogCategory>('PUT', `/blog/categories/${slug}/`, { body: data });
  return response;
}

  /**
 * Delete category
 * 
 * Delete a category
 */
async destroy(slug: string): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/blog/categories/${slug}/`);
  return;
}

}