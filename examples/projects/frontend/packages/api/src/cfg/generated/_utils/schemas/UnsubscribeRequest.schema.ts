/**
 * Zod schema for UnsubscribeRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Simple serializer for unsubscribe.
 *  */
import { z } from 'zod'

/**
 * Simple serializer for unsubscribe.
 */
export const UnsubscribeRequestSchema = z.object({
  subscription_id: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type UnsubscribeRequest = z.infer<typeof UnsubscribeRequestSchema>