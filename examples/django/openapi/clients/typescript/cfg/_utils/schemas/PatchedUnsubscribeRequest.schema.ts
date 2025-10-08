/**
 * Zod schema for PatchedUnsubscribeRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Simple serializer for unsubscribe.
 *  */
import { z } from 'zod'

/**
 * Simple serializer for unsubscribe.
 */
export const PatchedUnsubscribeRequestSchema = z.object({
  subscription_id: z.number().int().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedUnsubscribeRequest = z.infer<typeof PatchedUnsubscribeRequestSchema>