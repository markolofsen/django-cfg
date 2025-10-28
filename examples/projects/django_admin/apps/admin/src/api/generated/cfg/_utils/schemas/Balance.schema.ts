/**
 * Zod schema for Balance
 *
 * This schema provides runtime validation and type inference.
 *  * User balance serializer.
 *  */
import { z } from 'zod'

/**
 * User balance serializer.
 */
export const BalanceSchema = z.object({
  balance_usd: z.string(),
  balance_display: z.string(),
  total_deposited: z.string(),
  total_withdrawn: z.string(),
  last_transaction_at: z.iso.datetime().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Balance = z.infer<typeof BalanceSchema>