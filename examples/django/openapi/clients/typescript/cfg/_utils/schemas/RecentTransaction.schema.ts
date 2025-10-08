/**
 * Zod schema for RecentTransaction
 *
 * This schema provides runtime validation and type inference.
 *  * Recent transaction item
 *  */
import { z } from 'zod'

/**
 * Recent transaction item
 */
export const RecentTransactionSchema = z.object({
  id: z.string().uuid(),
  transaction_type: z.string(),
  amount_usd: z.number(),
  amount_display: z.string(),
  balance_after: z.number(),
  description: z.string(),
  created_at: z.string().datetime(),
  payment_id: z.string().nullable(),
  is_credit: z.boolean(),
  is_debit: z.boolean(),
  type_color: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RecentTransaction = z.infer<typeof RecentTransactionSchema>