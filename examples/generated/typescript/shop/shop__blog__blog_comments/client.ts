import * as Models from "./models";


/**
 * API endpoints for Blog - Comments.
 */
export class ShopBlogCommentsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(post_slug: string, author?: number, is_approved?: boolean, ordering?: string, page?: number, page_size?: number, parent?: number, post?: number): Promise<Models.PaginatedCommentList[]>;
  async list(post_slug: string, params?: { author?: number; is_approved?: boolean; ordering?: string; page?: number; page_size?: number; parent?: number; post?: number }): Promise<Models.PaginatedCommentList[]>;

  /**
   * List comments
   * 
   * Get a list of comments
   */
  async list(...args: any[]): Promise<Models.PaginatedCommentList[]> {
    const post_slug = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { author: args[1], is_approved: args[2], ordering: args[3], page: args[4], page_size: args[5], parent: args[6], post: args[7] };
    }
    const response = await this.client.request('GET', `/blog/comments/`, { params });
    return (response as any).results || [];
  }

  /**
   * Create comment
   * 
   * Create a new comment
   */
  async create(post_slug: string, data: Models.CommentRequest): Promise<Models.Comment> {
    const response = await this.client.request('POST', `/blog/comments/`, { body: data });
    return response;
  }

  /**
   * Get comment
   * 
   * Get details of a specific comment
   */
  async retrieve(id: number): Promise<Models.Comment> {
    const response = await this.client.request('GET', `/blog/comments/${id}/`);
    return response;
  }

  /**
   * Update comment
   * 
   * Update comment content
   */
  async update(id: number, data: Models.CommentRequest): Promise<Models.Comment> {
    const response = await this.client.request('PUT', `/blog/comments/${id}/`, { body: data });
    return response;
  }

  /**
   * Partially update comment
   * 
   * Partially update comment content
   */
  async partialUpdate(id: number, data?: Models.PatchedCommentRequest): Promise<Models.Comment> {
    const response = await this.client.request('PATCH', `/blog/comments/${id}/`, { body: data });
    return response;
  }

  /**
   * Delete comment
   * 
   * Delete a comment
   */
  async destroy(id: number): Promise<void> {
    const response = await this.client.request('DELETE', `/blog/comments/${id}/`);
    return;
  }

  async blogPostsCommentsList(post_slug: string, author?: number, is_approved?: boolean, ordering?: string, page?: number, page_size?: number, parent?: number, post?: number): Promise<Models.PaginatedCommentList[]>;
  async blogPostsCommentsList(post_slug: string, params?: { author?: number; is_approved?: boolean; ordering?: string; page?: number; page_size?: number; parent?: number; post?: number }): Promise<Models.PaginatedCommentList[]>;

  /**
   * List comments
   * 
   * Get a list of comments
   */
  async blogPostsCommentsList(...args: any[]): Promise<Models.PaginatedCommentList[]> {
    const post_slug = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { author: args[1], is_approved: args[2], ordering: args[3], page: args[4], page_size: args[5], parent: args[6], post: args[7] };
    }
    const response = await this.client.request('GET', `/blog/posts/${post_slug}/comments/`, { params });
    return (response as any).results || [];
  }

  /**
   * Create comment
   * 
   * Create a new comment
   */
  async blogPostsCommentsCreate(post_slug: string, data: Models.CommentRequest): Promise<Models.Comment> {
    const response = await this.client.request('POST', `/blog/posts/${post_slug}/comments/`, { body: data });
    return response;
  }

  /**
   * Get comment
   * 
   * Get details of a specific comment
   */
  async blogPostsCommentsRetrieve(id: number, post_slug: string): Promise<Models.Comment> {
    const response = await this.client.request('GET', `/blog/posts/${post_slug}/comments/${id}/`);
    return response;
  }

  /**
   * Update comment
   * 
   * Update comment content
   */
  async blogPostsCommentsUpdate(id: number, post_slug: string, data: Models.CommentRequest): Promise<Models.Comment> {
    const response = await this.client.request('PUT', `/blog/posts/${post_slug}/comments/${id}/`, { body: data });
    return response;
  }

  /**
   * Partially update comment
   * 
   * Partially update comment content
   */
  async blogPostsCommentsPartialUpdate(id: number, post_slug: string, data?: Models.PatchedCommentRequest): Promise<Models.Comment> {
    const response = await this.client.request('PATCH', `/blog/posts/${post_slug}/comments/${id}/`, { body: data });
    return response;
  }

  /**
   * Delete comment
   * 
   * Delete a comment
   */
  async blogPostsCommentsDestroy(id: number, post_slug: string): Promise<void> {
    const response = await this.client.request('DELETE', `/blog/posts/${post_slug}/comments/${id}/`);
    return;
  }

}