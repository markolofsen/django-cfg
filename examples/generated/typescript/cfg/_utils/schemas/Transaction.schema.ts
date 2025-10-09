/**
 * Zod schema for Transaction
 *
 * This schema provides runtime validation and type inference.
 *  * Transaction serializer with full details.

Used for transaction history and details.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Transaction serializer with full details.

Used for transaction history and details.
 */
export const TransactionSchema = z.object({
  id: z.string().uuid(),
  user: z.string(),
  amount_usd: z.number(),
  amount_display: z.string(),
  transaction_type: z.nativeEnum(Enums.TransactionTransactionType),
  type_color: z.string(),
  description: z.string(),
  payment_id: z.string().optional(),
  metadata: z.string(),
  is_credit: z.boolean(),
  is_debit: z.boolean(),
  created_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Transaction = z.infer<typeof TransactionSchema>