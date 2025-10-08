/**
 * SWR Hooks for Blog - Posts
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
import type { BlogStats } from '../schemas/BlogStats.schema'
import type { PaginatedPostLikeList } from '../schemas/PaginatedPostLikeList.schema'
import type { PaginatedPostListList } from '../schemas/PaginatedPostListList.schema'
import type { PostCreate } from '../schemas/PostCreate.schema'
import type { PostCreateRequest } from '../schemas/PostCreateRequest.schema'
import type { PostDetail } from '../schemas/PostDetail.schema'
import type { PostDetailRequest } from '../schemas/PostDetailRequest.schema'
import type { PostUpdate } from '../schemas/PostUpdate.schema'
import type { PostUpdateRequest } from '../schemas/PostUpdateRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List posts
 *
 * @method GET
 * @path /blog/posts/
 */
export function useBlogPosts(params?: { author?: number; category?: number; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tags?: any[] }) {
  return useSWR<PaginatedPostListList>(
    params ? ['blog-posts', params] : 'blog-posts',
    () => Fetchers.getBlogPosts(params)
  )
}

/**
 * Get post
 *
 * @method GET
 * @path /blog/posts/{slug}/
 */
export function useBlogPost(slug: string) {
  return useSWR<PostDetail>(
    ['blog-post', slug],
    () => Fetchers.getBlogPost(slug)
  )
}

/**
 * Get post likes
 *
 * @method GET
 * @path /blog/posts/{slug}/likes/
 */
export function useBlogPostsLikes(slug: string, params?: { author?: number; category?: number; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tags?: any[] }) {
  return useSWR<PaginatedPostLikeList>(
    ['blog-posts-likes', slug],
    () => Fetchers.getBlogPostsLikes(slug, params)
  )
}

/**
 * Get featured posts
 *
 * @method GET
 * @path /blog/posts/featured/
 */
export function useBlogPostsFeatured() {
  return useSWR<PostDetail>(
    'blog-posts-featured',
    () => Fetchers.getBlogPostsFeatured()
  )
}

/**
 * Get blog statistics
 *
 * @method GET
 * @path /blog/posts/stats/
 */
export function useBlogPostsStat() {
  return useSWR<BlogStats>(
    'blog-posts-stat',
    () => Fetchers.getBlogPostsStat()
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Create post
 *
 * @method POST
 * @path /blog/posts/
 */
export function useCreateBlogPosts() {
  const { mutate } = useSWRConfig()

  return async (data: PostCreateRequest): Promise<PostCreate> => {
    const result = await Fetchers.createBlogPosts(data)

    // Revalidate related queries
    mutate('blog-posts')

    return result
  }
}

/**
 * Update post
 *
 * @method PUT
 * @path /blog/posts/{slug}/
 */
export function useUpdateBlogPosts() {
  const { mutate } = useSWRConfig()

  return async (slug: string, data: PostUpdateRequest): Promise<PostUpdate> => {
    const result = await Fetchers.updateBlogPosts(slug, data)

    // Revalidate related queries
    mutate('blog-posts')
    mutate('blog-post')

    return result
  }
}

/**
 * Delete post
 *
 * @method DELETE
 * @path /blog/posts/{slug}/
 */
export function useDeleteBlogPosts() {
  const { mutate } = useSWRConfig()

  return async (slug: string): Promise<void> => {
    const result = await Fetchers.deleteBlogPosts(slug)

    // Revalidate related queries
    mutate('blog-posts')
    mutate('blog-post')

    return result
  }
}

/**
 * Like/unlike post
 *
 * @method POST
 * @path /blog/posts/{slug}/like/
 */
export function useCreateBlogPostsLike() {
  const { mutate } = useSWRConfig()

  return async (slug: string, data: PostDetailRequest): Promise<PostDetail> => {
    const result = await Fetchers.createBlogPostsLike(slug, data)

    // Revalidate related queries
    mutate('blog-posts-like')

    return result
  }
}
