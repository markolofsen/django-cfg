/**
 * Zod schema for PaymentOverview
 *
 * This schema provides runtime validation and type inference.
 *  * Payments overview metrics
 *  */
import { z } from 'zod'

/**
 * Payments overview metrics
 */
export const PaymentOverviewSchema = z.object({
  total_payments: z.number().int(),
  completed_payments: z.number().int(),
  pending_payments: z.number().int(),
  failed_payments: z.number().int(),
  total_amount_usd: z.number(),
  completed_amount_usd: z.number(),
  average_payment_usd: z.number(),
  success_rate: z.number(),
  last_payment_at: z.string().datetime().nullable(),
  payments_this_month: z.number().int(),
  amount_this_month: z.number(),
  top_currency: z.string().nullable(),
  top_currency_count: z.number().int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentOverview = z.infer<typeof PaymentOverviewSchema>