/**
 * Typed fetchers for Blog - Comments
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { CommentSchema, type Comment } from '../schemas/Comment.schema'
import { CommentRequestSchema, type CommentRequest } from '../schemas/CommentRequest.schema'
import { PaginatedCommentListSchema, type PaginatedCommentList } from '../schemas/PaginatedCommentList.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List comments
 *
 * Get a list of comments
 *
 * @method GET
 * @path /blog/comments/
 */
export async function getBlogCommentsList(
  post_slug: string, params?: { author?: number; is_approved?: boolean; ordering?: string; page?: number; page_size?: number; parent?: number; post?: number },
  client?: API
): Promise<PaginatedCommentList> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.list(post_slug, params?.author, params?.is_approved, params?.ordering, params?.page, params?.page_size, params?.parent, params?.post)
  return PaginatedCommentListSchema.parse(response)
}

/**
 * Create comment
 *
 * Create a new comment
 *
 * @method POST
 * @path /blog/comments/
 */
export async function createBlogComments(
  post_slug: string, data: CommentRequest,
  client?: API
): Promise<Comment> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.create(post_slug, data)
  return CommentSchema.parse(response)
}

/**
 * Get comment
 *
 * Get details of a specific comment
 *
 * @method GET
 * @path /blog/comments/{id}/
 */
export async function getBlogCommentsById(
  id: number,
  client?: API
): Promise<Comment> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.retrieve(id)
  return CommentSchema.parse(response)
}

/**
 * Update comment
 *
 * Update comment content
 *
 * @method PUT
 * @path /blog/comments/{id}/
 */
export async function updateBlogComments(
  id: number, data: CommentRequest,
  client?: API
): Promise<Comment> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.update(id, data)
  return CommentSchema.parse(response)
}

/**
 * Partially update comment
 *
 * Partially update comment content
 *
 * @method PATCH
 * @path /blog/comments/{id}/
 */
export async function partialUpdateBlogComments(
  id: number,
  client?: API
): Promise<Comment> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.partialUpdate(id)
  return CommentSchema.parse(response)
}

/**
 * Delete comment
 *
 * Delete a comment
 *
 * @method DELETE
 * @path /blog/comments/{id}/
 */
export async function deleteBlogComments(
  id: number,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.destroy(id)
  return response
}

/**
 * List comments
 *
 * Get a list of comments
 *
 * @method GET
 * @path /blog/posts/{post_slug}/comments/
 */
export async function getBlogPostsCommentsList(
  post_slug: string, params?: { author?: number; is_approved?: boolean; ordering?: string; page?: number; page_size?: number; parent?: number; post?: number },
  client?: API
): Promise<PaginatedCommentList> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.blogPostsCommentsList(post_slug, params?.author, params?.is_approved, params?.ordering, params?.page, params?.page_size, params?.parent, params?.post)
  return PaginatedCommentListSchema.parse(response)
}

/**
 * Create comment
 *
 * Create a new comment
 *
 * @method POST
 * @path /blog/posts/{post_slug}/comments/
 */
export async function createBlogPostsComments(
  post_slug: string, data: CommentRequest,
  client?: API
): Promise<Comment> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.blogPostsCommentsCreate(post_slug, data)
  return CommentSchema.parse(response)
}

/**
 * Get comment
 *
 * Get details of a specific comment
 *
 * @method GET
 * @path /blog/posts/{post_slug}/comments/{id}/
 */
export async function getBlogPostsCommentsById(
  id: number, post_slug: string,
  client?: API
): Promise<Comment> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.blogPostsCommentsRetrieve(id, post_slug)
  return CommentSchema.parse(response)
}

/**
 * Update comment
 *
 * Update comment content
 *
 * @method PUT
 * @path /blog/posts/{post_slug}/comments/{id}/
 */
export async function updateBlogPostsComments(
  id: number, post_slug: string, data: CommentRequest,
  client?: API
): Promise<Comment> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.blogPostsCommentsUpdate(id, post_slug, data)
  return CommentSchema.parse(response)
}

/**
 * Partially update comment
 *
 * Partially update comment content
 *
 * @method PATCH
 * @path /blog/posts/{post_slug}/comments/{id}/
 */
export async function partialUpdateBlogPostsComments(
  id: number, post_slug: string,
  client?: API
): Promise<Comment> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.blogPostsCommentsPartialUpdate(id, post_slug)
  return CommentSchema.parse(response)
}

/**
 * Delete comment
 *
 * Delete a comment
 *
 * @method DELETE
 * @path /blog/posts/{post_slug}/comments/{id}/
 */
export async function deleteBlogPostsComments(
  id: number, post_slug: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_comments.blogPostsCommentsDestroy(id, post_slug)
  return response
}

