/**
 * Zod schema for PaymentsMetrics
 *
 * This schema provides runtime validation and type inference.
 *  * Complete payments dashboard metrics
 *  */
import { z } from 'zod'
import { APIKeysOverviewSchema } from './APIKeysOverview.schema'
import { BalanceOverviewSchema } from './BalanceOverview.schema'
import { PaymentOverviewSchema } from './PaymentOverview.schema'
import { SubscriptionOverviewSchema } from './SubscriptionOverview.schema'

/**
 * Complete payments dashboard metrics
 */
export const PaymentsMetricsSchema = z.object({
  balance: BalanceOverviewSchema,
  subscription: SubscriptionOverviewSchema,
  api_keys: APIKeysOverviewSchema,
  payments: PaymentOverviewSchema,
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentsMetrics = z.infer<typeof PaymentsMetricsSchema>