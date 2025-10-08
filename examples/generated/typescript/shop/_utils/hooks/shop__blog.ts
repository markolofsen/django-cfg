/**
 * SWR Hooks for Blog
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
import type { BlogCategory } from '../schemas/BlogCategory.schema'
import type { PatchedBlogCategoryRequest } from '../schemas/PatchedBlogCategoryRequest.schema'
import type { PatchedPostUpdateRequest } from '../schemas/PatchedPostUpdateRequest.schema'
import type { PatchedTagRequest } from '../schemas/PatchedTagRequest.schema'
import type { PostUpdate } from '../schemas/PostUpdate.schema'
import type { Tag } from '../schemas/Tag.schema'
import type { TagRequest } from '../schemas/TagRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 *
 * @method GET
 * @path /blog/tags/{slug}/
 */
export function useBlogTag(slug: string) {
  return useSWR<Tag>(
    ['blog-tag', slug],
    () => Fetchers.getBlogTag(slug)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method PATCH
 * @path /blog/categories/{slug}/
 */
export function usePartialUpdateBlogCategories() {
  const { mutate } = useSWRConfig()

  return async (slug: string): Promise<BlogCategory> => {
    const result = await Fetchers.partialUpdateBlogCategories(slug)

    // Revalidate related queries
    mutate('blog-categories-partial')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /blog/posts/{slug}/
 */
export function usePartialUpdateBlogPosts() {
  const { mutate } = useSWRConfig()

  return async (slug: string): Promise<PostUpdate> => {
    const result = await Fetchers.partialUpdateBlogPosts(slug)

    // Revalidate related queries
    mutate('blog-posts-partial')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /blog/tags/{slug}/
 */
export function useUpdateBlogTags() {
  const { mutate } = useSWRConfig()

  return async (slug: string, data: TagRequest): Promise<Tag> => {
    const result = await Fetchers.updateBlogTags(slug, data)

    // Revalidate related queries
    mutate('blog-tags')
    mutate('blog-tag')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /blog/tags/{slug}/
 */
export function usePartialUpdateBlogTags() {
  const { mutate } = useSWRConfig()

  return async (slug: string): Promise<Tag> => {
    const result = await Fetchers.partialUpdateBlogTags(slug)

    // Revalidate related queries
    mutate('blog-tags-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /blog/tags/{slug}/
 */
export function useDeleteBlogTags() {
  const { mutate } = useSWRConfig()

  return async (slug: string): Promise<void> => {
    const result = await Fetchers.deleteBlogTags(slug)

    // Revalidate related queries
    mutate('blog-tags')
    mutate('blog-tag')

    return result
  }
}
