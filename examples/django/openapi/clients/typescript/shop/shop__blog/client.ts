import * as Models from "./models";


/**
 * API endpoints for Blog.
 */
export class ShopBlogAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * ViewSet for blog categories.
 */
async categoriesPartialUpdate(slug: string, data?: Models.PatchedBlogCategoryRequest): Promise<Models.BlogCategory> {
  const response = await this.client.request<Models.BlogCategory>('PATCH', `/blog/categories/${slug}/`, { body: data });
  return response;
}

  /**
 * ViewSet for blog posts.
 */
async postsPartialUpdate(slug: string, data?: Models.PatchedPostUpdateRequest): Promise<Models.PostUpdate> {
  const response = await this.client.request<Models.PostUpdate>('PATCH', `/blog/posts/${slug}/`, { body: data });
  return response;
}

  /**
 * ViewSet for blog tags.
 */
async tagsRetrieve(slug: string): Promise<Models.Tag> {
  const response = await this.client.request<Models.Tag>('GET', `/blog/tags/${slug}/`);
  return response;
}

  /**
 * ViewSet for blog tags.
 */
async tagsUpdate(slug: string, data: Models.TagRequest): Promise<Models.Tag> {
  const response = await this.client.request<Models.Tag>('PUT', `/blog/tags/${slug}/`, { body: data });
  return response;
}

  /**
 * ViewSet for blog tags.
 */
async tagsPartialUpdate(slug: string, data?: Models.PatchedTagRequest): Promise<Models.Tag> {
  const response = await this.client.request<Models.Tag>('PATCH', `/blog/tags/${slug}/`, { body: data });
  return response;
}

  /**
 * ViewSet for blog tags.
 */
async tagsDestroy(slug: string): Promise<void> {
  const response = await this.client.request<void>('DELETE', `/blog/tags/${slug}/`);
  return;
}

}