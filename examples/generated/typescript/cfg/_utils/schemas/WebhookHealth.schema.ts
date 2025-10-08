/**
 * Zod schema for WebhookHealth
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for webhook health check response.
 *  */
import { z } from 'zod'

/**
 * Serializer for webhook health check response.
 */
export const WebhookHealthSchema = z.object({
  status: z.string().max(20),
  timestamp: z.string().datetime(),
  providers: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WebhookHealth = z.infer<typeof WebhookHealthSchema>