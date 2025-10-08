/**
 * SWR Hooks for Blog - Categories
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
import type { BlogCategoryRequest } from '../schemas/BlogCategoryRequest.schema'
import type { PaginatedBlogCategoryList } from '../schemas/PaginatedBlogCategoryList.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List categories
 *
 * @method GET
 * @path /blog/categories/
 */
export function useBlogCategoriesList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedBlogCategoryList>(
    params ? ['blog-categories', params] : 'blog-categories',
    () => Fetchers.getBlogCategoriesList(params)
  )
}

/**
 * Get category
 *
 * @method GET
 * @path /blog/categories/{slug}/
 */
export function useBlogCategoriesById(slug: string) {
  return useSWR<BlogCategory>(
    ['blog-categorie', slug],
    () => Fetchers.getBlogCategoriesById(slug)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 * Create category
 *
 * @method POST
 * @path /blog/categories/
 */
export function useCreateBlogCategories() {
  const { mutate } = useSWRConfig()

  return async (data: BlogCategoryRequest): Promise<BlogCategory> => {
    const result = await Fetchers.createBlogCategories(data)

    // Revalidate related queries
    mutate('blog-categories')

    return result
  }
}

/**
 * Update category
 *
 * @method PUT
 * @path /blog/categories/{slug}/
 */
export function useUpdateBlogCategories() {
  const { mutate } = useSWRConfig()

  return async (slug: string, data: BlogCategoryRequest): Promise<BlogCategory> => {
    const result = await Fetchers.updateBlogCategories(slug, data)

    // Revalidate related queries
    mutate('blog-categories')
    mutate('blog-categorie')

    return result
  }
}

/**
 * Delete category
 *
 * @method DELETE
 * @path /blog/categories/{slug}/
 */
export function useDeleteBlogCategories() {
  const { mutate } = useSWRConfig()

  return async (slug: string): Promise<void> => {
    const result = await Fetchers.deleteBlogCategories(slug)

    // Revalidate related queries
    mutate('blog-categories')
    mutate('blog-categorie')

    return result
  }
}
