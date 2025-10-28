/**
 * SWR Hooks for Trading
 *
 * React hooks powered by SWR for data fetching with automatic caching,
 * revalidation, and optimistic updates.
 *
 * Usage:
 * ```typescript
 * // Query hooks (GET)
 * const { data, error, isLoading } = useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = useCreateUser()
 * await createUser({ name: 'John', email: 'john@example.com' })
 * ```
 */
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/trading__api__trading'
import type { API } from '../../index'
import type { Order } from '../schemas/Order.schema'
import type { OrderCreate } from '../schemas/OrderCreate.schema'
import type { OrderCreateRequest } from '../schemas/OrderCreateRequest.schema'
import type { OrderRequest } from '../schemas/OrderRequest.schema'
import type { PaginatedOrderList } from '../schemas/PaginatedOrderList.schema'
import type { PaginatedPortfolioList } from '../schemas/PaginatedPortfolioList.schema'
import type { PatchedOrderRequest } from '../schemas/PatchedOrderRequest.schema'
import type { Portfolio } from '../schemas/Portfolio.schema'
import type { PortfolioStats } from '../schemas/PortfolioStats.schema'

/**
 * List orders
 *
 * @method GET
 * @path /api/trading/orders/
 */
export function useTradingOrdersList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedOrderList>> {
  return useSWR<PaginatedOrderList>(
    params ? ['trading-orders', params] : 'trading-orders',
    () => Fetchers.getTradingOrdersList(params, client)
  )
}


/**
 * Create order
 *
 * @method POST
 * @path /api/trading/orders/
 */
export function useCreateTradingOrdersCreate() {
  const { mutate } = useSWRConfig()

  return async (data: OrderCreateRequest, client?: API): Promise<OrderCreate> => {
    const result = await Fetchers.createTradingOrdersCreate(data, client)
    // Revalidate related queries
    mutate('trading-orders')
    return result
  }
}


/**
 * Get order
 *
 * @method GET
 * @path /api/trading/orders/{id}/
 */
export function useTradingOrdersRetrieve(id: number, client?: API): ReturnType<typeof useSWR<Order>> {
  return useSWR<Order>(
    ['trading-order', id],
    () => Fetchers.getTradingOrdersRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /api/trading/orders/{id}/
 */
export function useUpdateTradingOrdersUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: number, data: OrderRequest, client?: API): Promise<Order> => {
    const result = await Fetchers.updateTradingOrdersUpdate(id, data, client)
    // Revalidate related queries
    mutate('trading-orders')
    mutate('trading-order')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /api/trading/orders/{id}/
 */
export function usePartialUpdateTradingOrdersPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (id: number, data?: PatchedOrderRequest, client?: API): Promise<Order> => {
    const result = await Fetchers.partialUpdateTradingOrdersPartialUpdate(id, data, client)
    // Revalidate related queries
    mutate('trading-orders-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /api/trading/orders/{id}/
 */
export function useDeleteTradingOrdersDestroy() {
  const { mutate } = useSWRConfig()

  return async (id: number, client?: API): Promise<void> => {
    const result = await Fetchers.deleteTradingOrdersDestroy(id, client)
    // Revalidate related queries
    mutate('trading-orders')
    mutate('trading-order')
    return result
  }
}


/**
 * List portfolios
 *
 * @method GET
 * @path /api/trading/portfolios/
 */
export function useTradingPortfoliosList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedPortfolioList>> {
  return useSWR<PaginatedPortfolioList>(
    params ? ['trading-portfolios', params] : 'trading-portfolios',
    () => Fetchers.getTradingPortfoliosList(params, client)
  )
}


/**
 * Get portfolio
 *
 * @method GET
 * @path /api/trading/portfolios/{id}/
 */
export function useTradingPortfoliosRetrieve(id: number, client?: API): ReturnType<typeof useSWR<Portfolio>> {
  return useSWR<Portfolio>(
    ['trading-portfolio', id],
    () => Fetchers.getTradingPortfoliosRetrieve(id, client)
  )
}


/**
 * Get my portfolio
 *
 * @method GET
 * @path /api/trading/portfolios/me/
 */
export function useTradingPortfoliosMeRetrieve(client?: API): ReturnType<typeof useSWR<Portfolio>> {
  return useSWR<Portfolio>(
    'trading-portfolios-me',
    () => Fetchers.getTradingPortfoliosMeRetrieve(client)
  )
}


/**
 * Get portfolio statistics
 *
 * @method GET
 * @path /api/trading/portfolios/stats/
 */
export function useTradingPortfoliosStatsRetrieve(client?: API): ReturnType<typeof useSWR<PortfolioStats>> {
  return useSWR<PortfolioStats>(
    'trading-portfolios-stat',
    () => Fetchers.getTradingPortfoliosStatsRetrieve(client)
  )
}


