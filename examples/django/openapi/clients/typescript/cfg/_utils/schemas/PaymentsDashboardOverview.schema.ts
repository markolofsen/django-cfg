/**
 * Zod schema for PaymentsDashboardOverview
 *
 * This schema provides runtime validation and type inference.
 *  * Complete payments dashboard overview response
 *  */
import { z } from 'zod'
import { PaymentsChartResponseSchema } from './PaymentsChartResponse.schema'
import { PaymentsMetricsSchema } from './PaymentsMetrics.schema'
import { RecentPaymentSchema } from './RecentPayment.schema'
import { RecentTransactionSchema } from './RecentTransaction.schema'

/**
 * Complete payments dashboard overview response
 */
export const PaymentsDashboardOverviewSchema = z.object({
  metrics: PaymentsMetricsSchema,
  recent_payments: z.array(RecentPaymentSchema),
  recent_transactions: z.array(RecentTransactionSchema),
  chart_data: PaymentsChartResponseSchema,
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentsDashboardOverview = z.infer<typeof PaymentsDashboardOverviewSchema>