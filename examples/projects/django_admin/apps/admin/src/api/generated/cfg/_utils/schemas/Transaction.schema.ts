/**
 * Zod schema for Transaction
 *
 * This schema provides runtime validation and type inference.
 *  * Transaction serializer.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Transaction serializer.
 */
export const TransactionSchema = z.object({
  id: z.uuid(),
  transaction_type: z.nativeEnum(Enums.TransactionTransactionType),
  type_display: z.string(),
  amount_usd: z.string(),
  amount_display: z.string(),
  balance_after: z.string(),
  payment_id: z.string().nullable(),
  description: z.string(),
  created_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Transaction = z.infer<typeof TransactionSchema>