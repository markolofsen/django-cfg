/**
 * Zod schema for PaymentRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Complete payment serializer with full details.

Used for detail views and updates.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Complete payment serializer with full details.

Used for detail views and updates.
 */
export const PaymentRequestSchema = z.object({
  amount_usd: z.number().min(1.0).max(50000.0),
  currency: z.number().int(),
  network: z.number().int().optional(),
  provider: z.nativeEnum(Enums.PaymentRequestProvider).optional(),
  status: z.nativeEnum(Enums.PaymentRequestStatus).optional(),
  callback_url: z.string().url().max(200).optional(),
  cancel_url: z.string().url().max(200).optional(),
  description: z.string().optional(),
  expires_at: z.string().datetime().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentRequest = z.infer<typeof PaymentRequestSchema>