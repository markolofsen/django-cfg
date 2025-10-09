/**
 * Zod schema for PaymentList
 *
 * This schema provides runtime validation and type inference.
 *  * Lightweight serializer for payment lists.

Optimized for list views with minimal data.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Lightweight serializer for payment lists.

Optimized for list views with minimal data.
 */
export const PaymentListSchema = z.object({
  id: z.string().uuid(),
  amount_usd: z.number(),
  currency: z.number().int(),
  provider: z.nativeEnum(Enums.PaymentListProvider),
  status: z.nativeEnum(Enums.PaymentListStatus),
  status_display: z.string(),
  amount_display: z.string(),
  created_at: z.string().datetime(),
  expires_at: z.string().datetime().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentList = z.infer<typeof PaymentListSchema>