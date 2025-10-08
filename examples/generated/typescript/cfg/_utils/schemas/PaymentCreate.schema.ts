/**
 * Zod schema for PaymentCreate
 *
 * This schema provides runtime validation and type inference.
 *  * Payment creation serializer with Pydantic integration.

Validates input and delegates to PaymentService.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Payment creation serializer with Pydantic integration.

Validates input and delegates to PaymentService.
 */
export const PaymentCreateSchema = z.object({
  amount_usd: z.number().min(1.0).max(50000.0),
  currency_code: z.nativeEnum(Enums.PaymentCreateCurrencyCode),
  provider: z.nativeEnum(Enums.PaymentCreateProvider).optional(),
  callback_url: z.string().url().optional(),
  cancel_url: z.string().url().optional(),
  description: z.string().max(500).optional(),
  metadata: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentCreate = z.infer<typeof PaymentCreateSchema>