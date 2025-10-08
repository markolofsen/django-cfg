/**
 * SWR Hooks for Shop - Products
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
import type { PaginatedProductListList } from '../schemas/PaginatedProductListList.schema'
import type { ProductDetail } from '../schemas/ProductDetail.schema'
import type { ShopStats } from '../schemas/ShopStats.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List products
 *
 * @method GET
 * @path /shop/products/
 */
export function useShopProductsList(params?: { category?: number; is_digital?: boolean; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string }) {
  return useSWR<PaginatedProductListList>(
    params ? ['shop-products', params] : 'shop-products',
    () => Fetchers.getShopProductsList(params)
  )
}

/**
 * Get product
 *
 * @method GET
 * @path /shop/products/{slug}/
 */
export function useShopProductsById(slug: string) {
  return useSWR<ProductDetail>(
    ['shop-product', slug],
    () => Fetchers.getShopProductsById(slug)
  )
}

/**
 * Get featured products
 *
 * @method GET
 * @path /shop/products/featured/
 */
export function useShopProductsFeaturedById() {
  return useSWR<ProductDetail>(
    'shop-products-featured',
    () => Fetchers.getShopProductsFeaturedById()
  )
}

/**
 * Get shop statistics
 *
 * @method GET
 * @path /shop/products/stats/
 */
export function useShopProductsStatsById() {
  return useSWR<ShopStats>(
    'shop-products-stat',
    () => Fetchers.getShopProductsStatsById()
  )
}
