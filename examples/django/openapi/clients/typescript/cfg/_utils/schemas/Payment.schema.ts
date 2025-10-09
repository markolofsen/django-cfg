/**
 * Zod schema for Payment
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
export const PaymentSchema = z.object({
  id: z.string().uuid(),
  user: z.string(),
  amount_usd: z.number().min(1.0).max(50000.0),
  currency: z.number().int(),
  network: z.number().int().optional(),
  provider: z.nativeEnum(Enums.PaymentProvider).optional(),
  status: z.nativeEnum(Enums.PaymentStatus).optional(),
  status_display: z.string(),
  amount_display: z.string(),
  provider_payment_id: z.string().optional(),
  payment_url: z.string().url().optional(),
  pay_address: z.string().optional(),
  callback_url: z.string().url().max(200).optional(),
  cancel_url: z.string().url().max(200).optional(),
  description: z.string().optional(),
  transaction_hash: z.string().optional(),
  confirmations_count: z.number().int(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  expires_at: z.string().datetime().optional(),
  completed_at: z.string().datetime().optional(),
  is_pending: z.boolean(),
  is_completed: z.boolean(),
  is_failed: z.boolean(),
  is_expired: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Payment = z.infer<typeof PaymentSchema>