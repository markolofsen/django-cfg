/**
 * Zod schema for WebhookResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for webhook processing response.

Standard response format for all webhook endpoints.
 *  */
import { z } from 'zod'

/**
 * Serializer for webhook processing response.

Standard response format for all webhook endpoints.
 */
export const WebhookResponseSchema = z.object({
  success: z.boolean(),
  message: z.string().max(500),
  payment_id: z.string().max(256).optional(),
  provider_payment_id: z.string().max(256).optional(),
  processed_at: z.string().datetime().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookResponse = z.infer<typeof WebhookResponseSchema>