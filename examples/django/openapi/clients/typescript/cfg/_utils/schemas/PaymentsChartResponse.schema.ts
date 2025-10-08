/**
 * Zod schema for PaymentsChartResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Complete chart response for payments analytics
 *  */
import { z } from 'zod'
import { ChartSeriesSchema } from './ChartSeries.schema'

/**
 * Complete chart response for payments analytics
 */
export const PaymentsChartResponseSchema = z.object({
  series: z.array(ChartSeriesSchema),
  period: z.string(),
  total_amount: z.number(),
  total_payments: z.number().int(),
  success_rate: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentsChartResponse = z.infer<typeof PaymentsChartResponseSchema>