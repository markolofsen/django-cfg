/**
 * Typed fetchers for Blog
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
import { BlogCategorySchema, type BlogCategory } from '../schemas/BlogCategory.schema'
import { PostUpdateSchema, type PostUpdate } from '../schemas/PostUpdate.schema'
import { TagSchema, type Tag } from '../schemas/Tag.schema'
import { TagRequestSchema, type TagRequest } from '../schemas/TagRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * partialUpdateBlogCategories
 *
 * ViewSet for blog categories.
 *
 * @method PATCH
 * @path /blog/categories/{slug}/
 */
export async function partialUpdateBlogCategories(
  slug: string,
  client?: API
): Promise<BlogCategory> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog.categoriesPartialUpdate(slug)
  return BlogCategorySchema.parse(response)
}

/**
 * partialUpdateBlogPosts
 *
 * ViewSet for blog posts.
 *
 * @method PATCH
 * @path /blog/posts/{slug}/
 */
export async function partialUpdateBlogPosts(
  slug: string,
  client?: API
): Promise<PostUpdate> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog.postsPartialUpdate(slug)
  return PostUpdateSchema.parse(response)
}

/**
 * getBlogTag
 *
 * ViewSet for blog tags.
 *
 * @method GET
 * @path /blog/tags/{slug}/
 */
export async function getBlogTag(
  slug: string,
  client?: API
): Promise<Tag> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog.tagsRetrieve(slug)
  return TagSchema.parse(response)
}

/**
 * updateBlogTags
 *
 * ViewSet for blog tags.
 *
 * @method PUT
 * @path /blog/tags/{slug}/
 */
export async function updateBlogTags(
  slug: string, data: TagRequest,
  client?: API
): Promise<Tag> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog.tagsUpdate(slug, data)
  return TagSchema.parse(response)
}

/**
 * partialUpdateBlogTags
 *
 * ViewSet for blog tags.
 *
 * @method PATCH
 * @path /blog/tags/{slug}/
 */
export async function partialUpdateBlogTags(
  slug: string,
  client?: API
): Promise<Tag> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog.tagsPartialUpdate(slug)
  return TagSchema.parse(response)
}

/**
 * deleteBlogTags
 *
 * ViewSet for blog tags.
 *
 * @method DELETE
 * @path /blog/tags/{slug}/
 */
export async function deleteBlogTags(
  slug: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog.tagsDestroy(slug)
  return response
}

