/**
 * SWR Hooks for Shop - Categories
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
import type { PaginatedShopCategoryList } from '../schemas/PaginatedShopCategoryList.schema'
import type { ShopCategory } from '../schemas/ShopCategory.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List categories
 *
 * @method GET
 * @path /shop/categories/
 */
export function useShopCategoriesList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }) {
  return useSWR<PaginatedShopCategoryList>(
    params ? ['shop-categories', params] : 'shop-categories',
    () => Fetchers.getShopCategoriesList(params)
  )
}

/**
 * Get category
 *
 * @method GET
 * @path /shop/categories/{slug}/
 */
export function useShopCategoriesById(slug: string) {
  return useSWR<ShopCategory>(
    ['shop-categorie', slug],
    () => Fetchers.getShopCategoriesById(slug)
  )
}
