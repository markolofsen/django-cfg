/**
 * SWR Hooks for Cfg Health
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
import type { HealthCheck } from '../schemas/HealthCheck.schema'
import type { QuickHealth } from '../schemas/QuickHealth.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 *
 * @method GET
 * @path /cfg/health/drf/
 */
export function useCfgHealthDrfById() {
  return useSWR<HealthCheck>(
    'cfg-health-drf',
    () => Fetchers.getCfgHealthDrfById()
  )
}

/**
 *
 * @method GET
 * @path /cfg/health/drf/quick/
 */
export function useCfgHealthDrfQuickById() {
  return useSWR<QuickHealth>(
    'cfg-health-drf-quick',
    () => Fetchers.getCfgHealthDrfQuickById()
  )
}
