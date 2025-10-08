/**
 * Typed fetchers for Blog - Tags
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
import { PaginatedTagListSchema, type PaginatedTagList } from '../schemas/PaginatedTagList.schema'
import { TagSchema, type Tag } from '../schemas/Tag.schema'
import { TagRequestSchema, type TagRequest } from '../schemas/TagRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List tags
 *
 * Get a list of all blog tags
 *
 * @method GET
 * @path /blog/tags/
 */
export async function getBlogTagsList(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedTagList> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_tags.list(params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedTagListSchema.parse(response)
}

/**
 * Create tag
 *
 * Create a new blog tag
 *
 * @method POST
 * @path /blog/tags/
 */
export async function createBlogTags(
  data: TagRequest,
  client?: API
): Promise<Tag> {
  const api = client || getAPIInstance()

  const response = await api.shop_blog_tags.create(data)
  return TagSchema.parse(response)
}

