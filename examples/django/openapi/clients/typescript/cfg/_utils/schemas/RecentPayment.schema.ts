/**
 * Zod schema for RecentPayment
 *
 * This schema provides runtime validation and type inference.
 *  * Recent payment item
 *  */
import { z } from 'zod'

/**
 * Recent payment item
 */
export const RecentPaymentSchema = z.object({
  id: z.string().uuid(),
  internal_payment_id: z.string(),
  amount_usd: z.number(),
  amount_display: z.string(),
  currency_code: z.string(),
  status: z.string(),
  status_display: z.string(),
  status_color: z.string(),
  provider: z.string(),
  created_at: z.string().datetime(),
  completed_at: z.string().datetime().optional(),
  is_pending: z.boolean(),
  is_completed: z.boolean(),
  is_failed: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RecentPayment = z.infer<typeof RecentPaymentSchema>