import * as Models from "./models";


/**
 * API endpoints for Blog - Comments.
 */
export class ShopBlogCommentsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * List comments
 * 
 * Get a list of comments
 */
async list(post_slug: string, author?: number | null, is_approved?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, parent?: number | null, post?: number | null): Promise<Models.PaginatedCommentList[]> {
  const response = await this.client.request<Models.PaginatedCommentList[]>('GET', `/blog/comments/`, { params: { author, is_approved, ordering, page, page_size, parent, post } });
  return (response as any).results || [];
}

  /**
 * Create comment
 * 
 * Create a new comment
 */
async create(post_slug: string, data: Models.CommentRequest): Promise<Models.Comment> {
  const response = await this.client.request<Models.Comment>('POST', `/blog/comments/`, { body: data });
  return response;
}

  /**
 * Get comment
 * 
 * Get details of a specific comment
 */
async retrieve(id: number): Promise<Models.Comment> {
  const response = await this.client.request<Models.Comment>('GET', `/blog/comments/${id}/`);
  return response;
}

  /**
 * Update comment
 * 
 * Update comment content
 */
async update(id: number, data: Models.CommentRequest): Promise<Models.Comment> {
  const response = await this.client.request<Models.Comment>('PUT', `/blog/comments/${id}/`, { body: data });
  return response;
}

  /**
 * Partially update comment
 * 
 * Partially update comment content
 */
async partialUpdate(id: number, data?: Models.PatchedCommentRequest): Promise<Models.Comment> {
  const response = await this.client.request<Models.Comment>('PATCH', `/blog/comments/${id}/`, { body: data });
  return response;
}

  /**
 * Delete comment
 * 
 * Delete a comment
 */
async destroy(id: number): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/blog/comments/${id}/`);
  return;
}

  /**
 * List comments
 * 
 * Get a list of comments
 */
async blogPostsCommentsList(post_slug: string, author?: number | null, is_approved?: boolean | null, ordering?: string | null, page?: number | null, page_size?: number | null, parent?: number | null, post?: number | null): Promise<Models.PaginatedCommentList[]> {
  const response = await this.client.request<Models.PaginatedCommentList[]>('GET', `/blog/posts/${post_slug}/comments/`, { params: { author, is_approved, ordering, page, page_size, parent, post } });
  return (response as any).results || [];
}

  /**
 * Create comment
 * 
 * Create a new comment
 */
async blogPostsCommentsCreate(post_slug: string, data: Models.CommentRequest): Promise<Models.Comment> {
  const response = await this.client.request<Models.Comment>('POST', `/blog/posts/${post_slug}/comments/`, { body: data });
  return response;
}

  /**
 * Get comment
 * 
 * Get details of a specific comment
 */
async blogPostsCommentsRetrieve(id: number, post_slug: string): Promise<Models.Comment> {
  const response = await this.client.request<Models.Comment>('GET', `/blog/posts/${post_slug}/comments/${id}/`);
  return response;
}

  /**
 * Update comment
 * 
 * Update comment content
 */
async blogPostsCommentsUpdate(id: number, post_slug: string, data: Models.CommentRequest): Promise<Models.Comment> {
  const response = await this.client.request<Models.Comment>('PUT', `/blog/posts/${post_slug}/comments/${id}/`, { body: data });
  return response;
}

  /**
 * Partially update comment
 * 
 * Partially update comment content
 */
async blogPostsCommentsPartialUpdate(id: number, post_slug: string, data?: Models.PatchedCommentRequest): Promise<Models.Comment> {
  const response = await this.client.request<Models.Comment>('PATCH', `/blog/posts/${post_slug}/comments/${id}/`, { body: data });
  return response;
}

  /**
 * Delete comment
 * 
 * Delete a comment
 */
async blogPostsCommentsDestroy(id: number, post_slug: string): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/blog/posts/${post_slug}/comments/${id}/`);
  return;
}

}