/**
 * Zod schema for PaymentCreateRequest
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
export const PaymentCreateRequestSchema = z.object({
  amount_usd: z.number().min(1.0).max(50000.0),
  currency_code: z.nativeEnum(Enums.PaymentCreateRequestCurrencyCode),
  provider: z.nativeEnum(Enums.PaymentCreateRequestProvider).optional(),
  callback_url: z.string().url().optional(),
  cancel_url: z.string().url().optional(),
  description: z.string().max(500).optional(),
  metadata: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentCreateRequest = z.infer<typeof PaymentCreateRequestSchema>