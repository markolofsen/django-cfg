import * as Models from "./models";


/**
 * API endpoints for Blog - Tags.
 */
export class ShopBlogTagsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List tags
 * 
 * Get a list of all blog tags
 */
async list(ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null): Promise<Models.PaginatedTagList[]> {
  const response = await this.client.request<Models.PaginatedTagList[]>('GET', "/blog/tags/", { params: { ordering, page, page_size, search } });
  return (response as any).results || [];
}

  /**
 * Create tag
 * 
 * Create a new blog tag
 */
async create(data: Models.TagRequest): Promise<Models.Tag> {
  const response = await this.client.request<Models.Tag>('POST', "/blog/tags/", { body: data });
  return response;
}

}