/**
 * Typed fetchers for Shop - Categories
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
import { PaginatedShopCategoryListSchema, type PaginatedShopCategoryList } from '../schemas/PaginatedShopCategoryList.schema'
import { ShopCategorySchema, type ShopCategory } from '../schemas/ShopCategory.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List categories
 *
 * Get a list of all shop categories
 *
 * @method GET
 * @path /shop/categories/
 */
export async function getShopCategories(
  params?: { ordering?: string; page?: number; page_size?: number; search?: string },
  client?: API
): Promise<PaginatedShopCategoryList> {
  const api = client || getAPIInstance()

  const response = await api.shop_categories.list(params?.ordering, params?.page, params?.page_size, params?.search)
  return PaginatedShopCategoryListSchema.parse(response)
}

/**
 * Get category
 *
 * Get details of a specific category
 *
 * @method GET
 * @path /shop/categories/{slug}/
 */
export async function getShopCategorie(
  slug: string,
  client?: API
): Promise<ShopCategory> {
  const api = client || getAPIInstance()

  const response = await api.shop_categories.retrieve(slug)
  return ShopCategorySchema.parse(response)
}

