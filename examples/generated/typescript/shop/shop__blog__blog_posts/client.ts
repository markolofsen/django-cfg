import * as Models from "./models";


/**
 * API endpoints for Blog - Posts.
 */
export class ShopBlogPostsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(author?: number, category?: number, is_featured?: boolean, ordering?: string, page?: number, page_size?: number, search?: string, status?: string, tags?: any[]): Promise<Models.PaginatedPostListList[]>;
  async list(params?: { author?: number; category?: number; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tags?: any[] }): Promise<Models.PaginatedPostListList[]>;

  /**
   * List posts
   * 
   * Get a paginated list of blog posts
   */
  async list(...args: any[]): Promise<Models.PaginatedPostListList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { author: args[0], category: args[1], is_featured: args[2], ordering: args[3], page: args[4], page_size: args[5], search: args[6], status: args[7], tags: args[8] };
    }
    const response = await this.client.request('GET', "/blog/posts/", { params });
    return (response as any).results || [];
  }

  /**
   * Create post
   * 
   * Create a new blog post
   */
  async create(data: Models.PostCreateRequest): Promise<Models.PostCreate> {
    const response = await this.client.request('POST', "/blog/posts/", { body: data });
    return response;
  }

  /**
   * Get post
   * 
   * Get detailed information about a specific post
   */
  async retrieve(slug: string): Promise<Models.PostDetail> {
    const response = await this.client.request('GET', `/blog/posts/${slug}/`);
    return response;
  }

  /**
   * Update post
   * 
   * Update post information
   */
  async update(slug: string, data: Models.PostUpdateRequest): Promise<Models.PostUpdate> {
    const response = await this.client.request('PUT', `/blog/posts/${slug}/`, { body: data });
    return response;
  }

  /**
   * Delete post
   * 
   * Delete a blog post
   */
  async destroy(slug: string): Promise<void> {
    const response = await this.client.request('DELETE', `/blog/posts/${slug}/`);
    return;
  }

  /**
   * Like/unlike post
   * 
   * Toggle like status for a post
   */
  async likeCreate(slug: string, data: Models.PostDetailRequest): Promise<Models.PostDetail> {
    const response = await this.client.request('POST', `/blog/posts/${slug}/like/`, { body: data });
    return response;
  }

  async likesList(slug: string, author?: number, category?: number, is_featured?: boolean, ordering?: string, page?: number, page_size?: number, search?: string, status?: string, tags?: any[]): Promise<Models.PaginatedPostLikeList[]>;
  async likesList(slug: string, params?: { author?: number; category?: number; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tags?: any[] }): Promise<Models.PaginatedPostLikeList[]>;

  /**
   * Get post likes
   * 
   * Get all likes for a post
   */
  async likesList(...args: any[]): Promise<Models.PaginatedPostLikeList[]> {
    const slug = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { author: args[1], category: args[2], is_featured: args[3], ordering: args[4], page: args[5], page_size: args[6], search: args[7], status: args[8], tags: args[9] };
    }
    const response = await this.client.request('GET', `/blog/posts/${slug}/likes/`, { params });
    return (response as any).results || [];
  }

  /**
   * Get featured posts
   * 
   * Get featured blog posts
   */
  async featuredRetrieve(): Promise<Models.PostDetail> {
    const response = await this.client.request('GET', "/blog/posts/featured/");
    return response;
  }

  /**
   * Get blog statistics
   * 
   * Get comprehensive blog statistics
   */
  async statsRetrieve(): Promise<Models.BlogStats> {
    const response = await this.client.request('GET', "/blog/posts/stats/");
    return response;
  }

}