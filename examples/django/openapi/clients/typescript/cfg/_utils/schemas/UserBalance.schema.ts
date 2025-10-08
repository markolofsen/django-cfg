/**
 * Zod schema for UserBalance
 *
 * This schema provides runtime validation and type inference.
 *  * User balance serializer with computed fields.

Provides balance information with display helpers.
 *  */
import { z } from 'zod'

/**
 * User balance serializer with computed fields.

Provides balance information with display helpers.
 */
export const UserBalanceSchema = z.object({
  user: z.string(),
  balance_usd: z.number(),
  balance_display: z.string(),
  is_empty: z.boolean(),
  has_transactions: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type UserBalance = z.infer<typeof UserBalanceSchema>