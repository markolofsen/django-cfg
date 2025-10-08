/**
 * Typed fetchers for Shop - Orders
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
import { OrderDetailSchema, type OrderDetail } from '../schemas/OrderDetail.schema'
import { PaginatedOrderListListSchema, type PaginatedOrderListList } from '../schemas/PaginatedOrderListList.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List orders
 *
 * Get a list of orders (admin only)
 *
 * @method GET
 * @path /shop/orders/
 */
export async function getShopOrders(
  params?: { customer?: number; ordering?: string; page?: number; page_size?: number; search?: string; status?: string },
  client?: API
): Promise<PaginatedOrderListList> {
  const api = client || getAPIInstance()

  const response = await api.shop_orders.list(params?.customer, params?.ordering, params?.page, params?.page_size, params?.search, params?.status)
  return PaginatedOrderListListSchema.parse(response)
}

/**
 * Get order
 *
 * Get details of a specific order
 *
 * @method GET
 * @path /shop/orders/{id}/
 */
export async function getShopOrder(
  id: number,
  client?: API
): Promise<OrderDetail> {
  const api = client || getAPIInstance()

  const response = await api.shop_orders.retrieve(id)
  return OrderDetailSchema.parse(response)
}

