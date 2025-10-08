/**
 * Typed fetchers for Blog - Posts
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
import { BlogStatsSchema, type BlogStats } from '../schemas/BlogStats.schema'
import { PaginatedPostLikeListSchema, type PaginatedPostLikeList } from '../schemas/PaginatedPostLikeList.schema'
import { PaginatedPostListListSchema, type PaginatedPostListList } from '../schemas/PaginatedPostListList.schema'
import { PostCreateSchema, type PostCreate } from '../schemas/PostCreate.schema'
import { PostCreateRequestSchema, type PostCreateRequest } from '../schemas/PostCreateRequest.schema'
import { PostDetailSchema, type PostDetail } from '../schemas/PostDetail.schema'
import { PostDetailRequestSchema, type PostDetailRequest } from '../schemas/PostDetailRequest.schema'
import { PostUpdateSchema, type PostUpdate } from '../schemas/PostUpdate.schema'
import { PostUpdateRequestSchema, type PostUpdateRequest } from '../schemas/PostUpdateRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List posts
 *
 * Get a paginated list of blog posts
 *
 * @method GET
 * @path /blog/posts/
 */
export async function getBlogPosts(
  params?: { author?: number; category?: number; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tags?: any[] },
  client?: API
): Promise<PaginatedPostListList> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.list(params?.author, params?.category, params?.is_featured, params?.ordering, params?.page, params?.page_size, params?.search, params?.status, params?.tags)
  return PaginatedPostListListSchema.parse(response)
}

/**
 * Create post
 *
 * Create a new blog post
 *
 * @method POST
 * @path /blog/posts/
 */
export async function createBlogPosts(
  data: PostCreateRequest,
  client?: API
): Promise<PostCreate> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.create(data)
  return PostCreateSchema.parse(response)
}

/**
 * Get post
 *
 * Get detailed information about a specific post
 *
 * @method GET
 * @path /blog/posts/{slug}/
 */
export async function getBlogPost(
  slug: string,
  client?: API
): Promise<PostDetail> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.retrieve(slug)
  return PostDetailSchema.parse(response)
}

/**
 * Update post
 *
 * Update post information
 *
 * @method PUT
 * @path /blog/posts/{slug}/
 */
export async function updateBlogPosts(
  slug: string, data: PostUpdateRequest,
  client?: API
): Promise<PostUpdate> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.update(slug, data)
  return PostUpdateSchema.parse(response)
}

/**
 * Delete post
 *
 * Delete a blog post
 *
 * @method DELETE
 * @path /blog/posts/{slug}/
 */
export async function deleteBlogPosts(
  slug: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.destroy(slug)
  return response
}

/**
 * Like/unlike post
 *
 * Toggle like status for a post
 *
 * @method POST
 * @path /blog/posts/{slug}/like/
 */
export async function createBlogPostsLike(
  slug: string, data: PostDetailRequest,
  client?: API
): Promise<PostDetail> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.likeCreate(slug, data)
  return PostDetailSchema.parse(response)
}

/**
 * Get post likes
 *
 * Get all likes for a post
 *
 * @method GET
 * @path /blog/posts/{slug}/likes/
 */
export async function getBlogPostsLikes(
  slug: string, params?: { author?: number; category?: number; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string; tags?: any[] },
  client?: API
): Promise<PaginatedPostLikeList> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.likesList(slug, params?.author, params?.category, params?.is_featured, params?.ordering, params?.page, params?.page_size, params?.search, params?.status, params?.tags)
  return PaginatedPostLikeListSchema.parse(response)
}

/**
 * Get featured posts
 *
 * Get featured blog posts
 *
 * @method GET
 * @path /blog/posts/featured/
 */
export async function getBlogPostsFeatured(
  client?: API
): Promise<PostDetail> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.featuredRetrieve()
  return PostDetailSchema.parse(response)
}

/**
 * Get blog statistics
 *
 * Get comprehensive blog statistics
 *
 * @method GET
 * @path /blog/posts/stats/
 */
export async function getBlogPostsStat(
  client?: API
): Promise<BlogStats> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_posts.statsRetrieve()
  return BlogStatsSchema.parse(response)
}

