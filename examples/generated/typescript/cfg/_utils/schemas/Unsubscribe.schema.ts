/**
 * Zod schema for Unsubscribe
 *
 * This schema provides runtime validation and type inference.
 *  * Simple serializer for unsubscribe.
 *  */
import { z } from 'zod'

/**
 * Simple serializer for unsubscribe.
 */
export const UnsubscribeSchema = z.object({
  subscription_id: z.number().int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Unsubscribe = z.infer<typeof UnsubscribeSchema>