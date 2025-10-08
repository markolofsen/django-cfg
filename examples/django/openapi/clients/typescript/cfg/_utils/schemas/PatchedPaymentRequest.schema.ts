/**
 * Zod schema for PatchedPaymentRequest
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
export const PatchedPaymentRequestSchema = z.object({
  amount_usd: z.number().min(1.0).max(50000.0).optional(),
  currency: z.number().int().optional(),
  network: z.number().int().optional().nullable(),
  provider: z.nativeEnum(Enums.PatchedPaymentRequestProvider).optional(),
  status: z.nativeEnum(Enums.PatchedPaymentRequestStatus).optional(),
  callback_url: z.string().url().max(200).optional().nullable(),
  cancel_url: z.string().url().max(200).optional().nullable(),
  description: z.string().optional(),
  expires_at: z.string().datetime().optional().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedPaymentRequest = z.infer<typeof PatchedPaymentRequestSchema>