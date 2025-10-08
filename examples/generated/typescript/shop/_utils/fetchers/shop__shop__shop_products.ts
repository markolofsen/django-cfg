/**
 * Typed fetchers for Shop - Products
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
import { PaginatedProductListListSchema, type PaginatedProductListList } from '../schemas/PaginatedProductListList.schema'
import { ProductDetailSchema, type ProductDetail } from '../schemas/ProductDetail.schema'
import { ShopStatsSchema, type ShopStats } from '../schemas/ShopStats.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List products
 *
 * Get a paginated list of products
 *
 * @method GET
 * @path /shop/products/
 */
export async function getShopProducts(
  params?: { category?: number; is_digital?: boolean; is_featured?: boolean; ordering?: string; page?: number; page_size?: number; search?: string; status?: string },
  client?: API
): Promise<PaginatedProductListList> {
  const api = client || getAPIInstance()

  const response = await api.shop_products.list(params?.category, params?.is_digital, params?.is_featured, params?.ordering, params?.page, params?.page_size, params?.search, params?.status)
  return PaginatedProductListListSchema.parse(response)
}

/**
 * Get product
 *
 * Get detailed information about a specific product
 *
 * @method GET
 * @path /shop/products/{slug}/
 */
export async function getShopProduct(
  slug: string,
  client?: API
): Promise<ProductDetail> {
  const api = client || getAPIInstance()

  const response = await api.shop_products.retrieve(slug)
  return ProductDetailSchema.parse(response)
}

/**
 * Get featured products
 *
 * Get featured products
 *
 * @method GET
 * @path /shop/products/featured/
 */
export async function getShopProductsFeatured(
  client?: API
): Promise<ProductDetail> {
  const api = client || getAPIInstance()

  const response = await api.shop_products.featuredRetrieve()
  return ProductDetailSchema.parse(response)
}

/**
 * Get shop statistics
 *
 * Get comprehensive shop statistics
 *
 * @method GET
 * @path /shop/products/stats/
 */
export async function getShopProductsStat(
  client?: API
): Promise<ShopStats> {
  const api = client || getAPIInstance()

  const response = await api.shop_products.statsRetrieve()
  return ShopStatsSchema.parse(response)
}

