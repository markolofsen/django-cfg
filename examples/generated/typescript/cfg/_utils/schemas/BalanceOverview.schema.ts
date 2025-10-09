/**
 * Zod schema for BalanceOverview
 *
 * This schema provides runtime validation and type inference.
 *  * User balance overview metrics
 *  */
import { z } from 'zod'

/**
 * User balance overview metrics
 */
export const BalanceOverviewSchema = z.object({
  current_balance: z.number(),
  balance_display: z.string(),
  total_deposited: z.number(),
  total_spent: z.number(),
  last_transaction_at: z.string().datetime().optional(),
  has_transactions: z.boolean(),
  is_empty: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type BalanceOverview = z.infer<typeof BalanceOverviewSchema>