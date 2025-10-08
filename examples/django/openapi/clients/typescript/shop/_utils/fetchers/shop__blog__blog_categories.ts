/**
 * Typed fetchers for Blog - Categories
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
import { BlogCategoryRequestSchema, type BlogCategoryRequest } from '../schemas/BlogCategoryRequest.schema'
import { PaginatedBlogCategoryListSchema, type PaginatedBlogCategoryList } from '../schemas/PaginatedBlogCategoryList.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List categories
 *
 * Get a list of all blog categories
 *
 * @method GET
 * @path /blog/categories/
 */
export async function getBlogCategoriesList(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedBlogCategoryList> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_categories.list(params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedBlogCategoryListSchema.parse(response)
}

/**
 * Create category
 *
 * Create a new blog category
 *
 * @method POST
 * @path /blog/categories/
 */
export async function createBlogCategories(
  data: BlogCategoryRequest,
  client?: API
): Promise<BlogCategory> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_categories.create(data)
  return BlogCategorySchema.parse(response)
}

/**
 * Get category
 *
 * Get details of a specific category
 *
 * @method GET
 * @path /blog/categories/{slug}/
 */
export async function getBlogCategoriesById(
  slug: string,
  client?: API
): Promise<BlogCategory> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_categories.retrieve(slug)
  return BlogCategorySchema.parse(response)
}

/**
 * Update category
 *
 * Update category information
 *
 * @method PUT
 * @path /blog/categories/{slug}/
 */
export async function updateBlogCategories(
  slug: string, data: BlogCategoryRequest,
  client?: API
): Promise<BlogCategory> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_categories.update(slug, data)
  return BlogCategorySchema.parse(response)
}

/**
 * Delete category
 *
 * Delete a category
 *
 * @method DELETE
 * @path /blog/categories/{slug}/
 */
export async function deleteBlogCategories(
  slug: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_categories.destroy(slug)
  return response
}

