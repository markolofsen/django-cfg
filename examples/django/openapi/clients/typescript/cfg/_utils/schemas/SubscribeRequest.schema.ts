/**
 * Zod schema for SubscribeRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Simple serializer for newsletter subscription.
 *  */
import { z } from 'zod'

/**
 * Simple serializer for newsletter subscription.
 */
export const SubscribeRequestSchema = z.object({
  newsletter_id: z.number().int(),
  email: z.string().email().min(1),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SubscribeRequest = z.infer<typeof SubscribeRequestSchema>