/**
 * Zod schema for SubscribeResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response for subscription.
 *  */
import { z } from 'zod'

/**
 * Response for subscription.
 */
export const SubscribeResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  subscription_id: z.number().int().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SubscribeResponse = z.infer<typeof SubscribeResponseSchema>