/**
 * Zod schema for PaymentList
 *
 * This schema provides runtime validation and type inference.
 *  * Payment list item (lighter than detail).
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Payment list item (lighter than detail).
 */
export const PaymentListSchema = z.object({
  id: z.uuid(),
  internal_payment_id: z.string(),
  amount_usd: z.string(),
  currency_code: z.string(),
  currency_token: z.string(),
  status: z.nativeEnum(Enums.PaymentListStatus),
  status_display: z.string(),
  created_at: z.iso.datetime(),
  completed_at: z.iso.datetime().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentList = z.infer<typeof PaymentListSchema>