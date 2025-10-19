/**
 * Typed fetchers for Trading
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
import { OrderSchema, type Order } from '../schemas/Order.schema'
import { OrderCreateSchema, type OrderCreate } from '../schemas/OrderCreate.schema'
import { OrderCreateRequestSchema, type OrderCreateRequest } from '../schemas/OrderCreateRequest.schema'
import { OrderRequestSchema, type OrderRequest } from '../schemas/OrderRequest.schema'
import { PaginatedOrderListSchema, type PaginatedOrderList } from '../schemas/PaginatedOrderList.schema'
import { PaginatedPortfolioListSchema, type PaginatedPortfolioList } from '../schemas/PaginatedPortfolioList.schema'
import { PatchedOrderRequestSchema, type PatchedOrderRequest } from '../schemas/PatchedOrderRequest.schema'
import { PortfolioSchema, type Portfolio } from '../schemas/Portfolio.schema'
import { PortfolioStatsSchema, type PortfolioStats } from '../schemas/PortfolioStats.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List orders
 *
 * @method GET
 * @path /api/trading/orders/
 */
export async function getTradingOrdersList(  params?: { page?: number; page_size?: number },  client?
): Promise<PaginatedOrderList> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.ordersList(params?.page, params?.page_size)
  return PaginatedOrderListSchema.parse(response)
}


/**
 * Create order
 *
 * @method POST
 * @path /api/trading/orders/
 */
export async function createTradingOrdersCreate(  data: OrderCreateRequest,  client?
): Promise<OrderCreate> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.ordersCreate(data)
  return OrderCreateSchema.parse(response)
}


/**
 * Get order
 *
 * @method GET
 * @path /api/trading/orders/{id}/
 */
export async function getTradingOrdersRetrieve(  id: number,  client?
): Promise<Order> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.ordersRetrieve(id)
  return OrderSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /api/trading/orders/{id}/
 */
export async function updateTradingOrdersUpdate(  id: number, data: OrderRequest,  client?
): Promise<Order> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.ordersUpdate(id, data)
  return OrderSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /api/trading/orders/{id}/
 */
export async function partialUpdateTradingOrdersPartialUpdate(  id: number, data?: PatchedOrderRequest,  client?
): Promise<Order> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.ordersPartialUpdate(id, data)
  return OrderSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /api/trading/orders/{id}/
 */
export async function deleteTradingOrdersDestroy(  id: number,  client?
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.ordersDestroy(id)
  return response
}


/**
 * List portfolios
 *
 * @method GET
 * @path /api/trading/portfolios/
 */
export async function getTradingPortfoliosList(  params?: { page?: number; page_size?: number },  client?
): Promise<PaginatedPortfolioList> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.portfoliosList(params?.page, params?.page_size)
  return PaginatedPortfolioListSchema.parse(response)
}


/**
 * Get portfolio
 *
 * @method GET
 * @path /api/trading/portfolios/{id}/
 */
export async function getTradingPortfoliosRetrieve(  id: number,  client?
): Promise<Portfolio> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.portfoliosRetrieve(id)
  return PortfolioSchema.parse(response)
}


/**
 * Get my portfolio
 *
 * @method GET
 * @path /api/trading/portfolios/me/
 */
export async function getTradingPortfoliosMeRetrieve(  client?
): Promise<Portfolio> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.portfoliosMeRetrieve()
  return PortfolioSchema.parse(response)
}


/**
 * Get portfolio statistics
 *
 * @method GET
 * @path /api/trading/portfolios/stats/
 */
export async function getTradingPortfoliosStatsRetrieve(  client?
): Promise<PortfolioStats> {
  const api = client || getAPIInstance()
  const response = await api.trading_trading.portfoliosStatsRetrieve()
  return PortfolioStatsSchema.parse(response)
}


