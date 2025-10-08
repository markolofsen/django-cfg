/**
 * SWR Hooks for Blog - Comments
 *
 * Auto-generated React hooks for data fetching with SWR.
 *
 * Setup:
 * ```typescript
 * // Configure API once (in your app root)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 * ```
 *
 * Usage:
 * ```typescript
 * // Query hook
 * const { data, error, mutate } = useShopProducts({ page: 1 })
 *
 * // Mutation hook
 * const createProduct = useCreateShopProduct()
 * await createProduct({ name: 'Product', price: 99 })
 * ```
 */
import type { Comment } from '../schemas/Comment.schema'
import type { CommentRequest } from '../schemas/CommentRequest.schema'
import type { PaginatedCommentList } from '../schemas/PaginatedCommentList.schema'
import type { PatchedCommentRequest } from '../schemas/PatchedCommentRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List comments
 *
 * @method GET
 * @path /blog/comments/
 */
export function useBlogComments(post_slug: string, params?: { author?: number; is_approved?: boolean; ordering?: string; page?: number; page_size?: number; parent?: number; post?: number }) {
  return useSWR<PaginatedCommentList>(
    ['blog-comments', post_slug],
    () => Fetchers.getBlogComments(post_slug, params)
  )
}

/**
 * Get comment
 *
 * @method GET
 * @path /blog/comments/{id}/
 */
export function useBlogComment(id: number) {
  return useSWR<Comment>(
    ['blog-comment', id],
    () => Fetchers.getBlogComment(id)
  )
}

/**
 * List comments
 *
 * @method GET
 * @path /blog/posts/{post_slug}/comments/
 */
export function useBlogPostsComments(post_slug: string, params?: { author?: number; is_approved?: boolean; ordering?: string; page?: number; page_size?: number; parent?: number; post?: number }) {
  return useSWR<PaginatedCommentList>(
    ['blog-posts-comments', post_slug],
    () => Fetchers.getBlogPostsComments(post_slug, params)
  )
}

/**
 * Get comment
 *
 * @method GET
 * @path /blog/posts/{post_slug}/comments/{id}/
 */
export function useBlogPostsComment(id: number, post_slug: string) {
  return useSWR<Comment>(
    ['blog-posts-comment', id],
    () => Fetchers.getBlogPostsComment(id, post_slug)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Create comment
 *
 * @method POST
 * @path /blog/comments/
 */
export function useCreateBlogComments() {
  const { mutate } = useSWRConfig()

  return async (post_slug: string, data: CommentRequest): Promise<Comment> => {
    const result = await Fetchers.createBlogComments(post_slug, data)

    // Revalidate related queries
    mutate('blog-comments')

    return result
  }
}

/**
 * Update comment
 *
 * @method PUT
 * @path /blog/comments/{id}/
 */
export function useUpdateBlogComments() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: CommentRequest): Promise<Comment> => {
    const result = await Fetchers.updateBlogComments(id, data)

    // Revalidate related queries
    mutate('blog-comments')
    mutate('blog-comment')

    return result
  }
}

/**
 * Partially update comment
 *
 * @method PATCH
 * @path /blog/comments/{id}/
 */
export function usePartialUpdateBlogComments() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<Comment> => {
    const result = await Fetchers.partialUpdateBlogComments(id)

    // Revalidate related queries
    mutate('blog-comments-partial')

    return result
  }
}

/**
 * Delete comment
 *
 * @method DELETE
 * @path /blog/comments/{id}/
 */
export function useDeleteBlogComments() {
  const { mutate } = useSWRConfig()

  return async (id: number): Promise<void> => {
    const result = await Fetchers.deleteBlogComments(id)

    // Revalidate related queries
    mutate('blog-comments')
    mutate('blog-comment')

    return result
  }
}

/**
 * Create comment
 *
 * @method POST
 * @path /blog/posts/{post_slug}/comments/
 */
export function useCreateBlogPostsComments() {
  const { mutate } = useSWRConfig()

  return async (post_slug: string, data: CommentRequest): Promise<Comment> => {
    const result = await Fetchers.createBlogPostsComments(post_slug, data)

    // Revalidate related queries
    mutate('blog-posts-comments')

    return result
  }
}

/**
 * Update comment
 *
 * @method PUT
 * @path /blog/posts/{post_slug}/comments/{id}/
 */
export function useUpdateBlogPostsComments() {
  const { mutate } = useSWRConfig()

  return async (id: number, post_slug: string, data: CommentRequest): Promise<Comment> => {
    const result = await Fetchers.updateBlogPostsComments(id, post_slug, data)

    // Revalidate related queries
    mutate('blog-posts-comments')
    mutate('blog-posts-comment')

    return result
  }
}

/**
 * Partially update comment
 *
 * @method PATCH
 * @path /blog/posts/{post_slug}/comments/{id}/
 */
export function usePartialUpdateBlogPostsComments() {
  const { mutate } = useSWRConfig()

  return async (id: number, post_slug: string): Promise<Comment> => {
    const result = await Fetchers.partialUpdateBlogPostsComments(id, post_slug)

    // Revalidate related queries
    mutate('blog-posts-comments-partial')

    return result
  }
}

/**
 * Delete comment
 *
 * @method DELETE
 * @path /blog/posts/{post_slug}/comments/{id}/
 */
export function useDeleteBlogPostsComments() {
  const { mutate } = useSWRConfig()

  return async (id: number, post_slug: string): Promise<void> => {
    const result = await Fetchers.deleteBlogPostsComments(id, post_slug)

    // Revalidate related queries
    mutate('blog-posts-comments')
    mutate('blog-posts-comment')

    return result
  }
}
