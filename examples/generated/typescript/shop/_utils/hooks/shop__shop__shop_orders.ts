/**
 * SWR Hooks for Shop - Orders
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
import type { OrderDetail } from '../schemas/OrderDetail.schema'
import type { PaginatedOrderListList } from '../schemas/PaginatedOrderListList.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 * List orders
 *
 * @method GET
 * @path /shop/orders/
 */
export function useShopOrders(params?: { customer?: number; ordering?: string; page?: number; page_size?: number; search?: string; status?: string }) {
  return useSWR<PaginatedOrderListList>(
    params ? ['shop-orders', params] : 'shop-orders',
    () => Fetchers.getShopOrders(params)
  )
}

/**
 * Get order
 *
 * @method GET
 * @path /shop/orders/{id}/
 */
export function useShopOrder(id: number) {
  return useSWR<OrderDetail>(
    ['shop-order', id],
    () => Fetchers.getShopOrder(id)
  )
}
