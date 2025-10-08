import * as Models from "./models";


/**
 * API endpoints for Blog - Tags.
 */
export class ShopBlogTagsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedTagList[]>;
  async list(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedTagList[]>;

  /**
   * List tags
   * 
   * Get a list of all blog tags
   */
  async list(...args: any[]): Promise<Models.PaginatedTagList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/blog/tags/", { params });
    return (response as any).results || [];
  }

  /**
   * Create tag
   * 
   * Create a new blog tag
   */
  async create(data: Models.TagRequest): Promise<Models.Tag> {
    const response = await this.client.request('POST', "/blog/tags/", { body: data });
    return response;
  }

}