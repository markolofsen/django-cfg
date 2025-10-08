/**
 * SWR Hooks for Blog - Tags
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
import type { PaginatedTagList } from '../schemas/PaginatedTagList.schema'
import type { Tag } from '../schemas/Tag.schema'
import type { TagRequest } from '../schemas/TagRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List tags
 *
 * @method GET
 * @path /blog/tags/
 */
export function useBlogTags(params?: { ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedTagList>(
    params ? ['blog-tags', params] : 'blog-tags',
    () => Fetchers.getBlogTags(params)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Create tag
 *
 * @method POST
 * @path /blog/tags/
 */
export function useCreateBlogTags() {
  const { mutate } = useSWRConfig()

  return async (data: TagRequest): Promise<Tag> => {
    const result = await Fetchers.createBlogTags(data)

    // Revalidate related queries
    mutate('blog-tags')

    return result
  }
}
