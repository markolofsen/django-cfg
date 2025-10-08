import * as Models from "./models";


/**
 * API endpoints for Blog - Posts.
 */
export class ShopBlogPostsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List posts
 * 
 * Get a paginated list of blog posts
 */
async list(author?: number | null, category?: number | null, is_featured?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null, status?: string | null, tags?: any[] | null): Promise<Models.PaginatedPostListList[]> {
  const response = await this.client.request<Models.PaginatedPostListList[]>('GET', "/blog/posts/", { params: { author, category, is_featured, ordering, page, page_size, search, status, tags } });
  return (response as any).results || [];
}

  /**
 * Create post
 * 
 * Create a new blog post
 */
async create(data: Models.PostCreateRequest): Promise<Models.PostCreate> {
  const response = await this.client.request<Models.PostCreate>('POST', "/blog/posts/", { body: data });
  return response;
}

  /**
 * Get post
 * 
 * Get detailed information about a specific post
 */
async retrieve(slug: string): Promise<Models.PostDetail> {
  const response = await this.client.request<Models.PostDetail>('GET', `/blog/posts/${slug}/`);
  return response;
}

  /**
 * Update post
 * 
 * Update post information
 */
async update(slug: string, data: Models.PostUpdateRequest): Promise<Models.PostUpdate> {
  const response = await this.client.request<Models.PostUpdate>('PUT', `/blog/posts/${slug}/`, { body: data });
  return response;
}

  /**
 * Delete post
 * 
 * Delete a blog post
 */
async destroy(slug: string): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/blog/posts/${slug}/`);
  return;
}

  /**
 * Like/unlike post
 * 
 * Toggle like status for a post
 */
async likeCreate(slug: string, data: Models.PostDetailRequest): Promise<Models.PostDetail> {
  const response = await this.client.request<Models.PostDetail>('POST', `/blog/posts/${slug}/like/`, { body: data });
  return response;
}

  /**
 * Get post likes
 * 
 * Get all likes for a post
 */
async likesList(slug: string, author?: number | null, category?: number | null, is_featured?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, search?: string | null, status?: string | null, tags?: any[] | null): Promise<Models.PaginatedPostLikeList[]> {
  const response = await this.client.request<Models.PaginatedPostLikeList[]>('GET', `/blog/posts/${slug}/likes/`, { params: { author, category, is_featured, ordering, page, page_size, search, status, tags } });
  return (response as any).results || [];
}

  /**
 * Get featured posts
 * 
 * Get featured blog posts
 */
async featuredRetrieve(): Promise<Models.PostDetail> {
  const response = await this.client.request<Models.PostDetail>('GET', "/blog/posts/featured/");
  return response;
}

  /**
 * Get blog statistics
 * 
 * Get comprehensive blog statistics
 */
async statsRetrieve(): Promise<Models.BlogStats> {
  const response = await this.client.request<Models.BlogStats>('GET', "/blog/posts/stats/");
  return response;
}

}