/**
 * Zod schema for WebhookResponseRequest
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
export const WebhookResponseRequestSchema = z.object({
  success: z.boolean(),
  message: z.string().min(1).max(500),
  payment_id: z.string().min(1).max(256).optional(),
  provider_payment_id: z.string().min(1).max(256).optional(),
  processed_at: z.string().datetime().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookResponseRequest = z.infer<typeof WebhookResponseRequestSchema>